"""
test/test_wallet_analyzer.py
Bộ kiểm thử tự động cho công cụ phân tích dòng tiền ví On-Chain (Lab 6)
Bao gồm tối thiểu 3 nhóm trường hợp:
1. Luồng nghiệp vụ bình thường (Normal Flow)
2. Kịch bản biên và trường hợp lỗi (Edge Cases)
3. Kịch bản tấn công gian lận (Adversarial / Fraud Case - Chuẩn Giỏi 9.0 - 10.0)
"""

import unittest
from datetime import datetime, timezone
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.wallet_analyzer import parse_and_process_transactions, WEI_IN_ETH


class TestWalletAnalyzer(unittest.TestCase):
    def setUp(self):
        self.target_address = "0x6f69897D262D99Fc705bF7549631ca1b498d1F14"
        self.now_ts = int(datetime.now(timezone.utc).timestamp())

    def test_01_normal_flow_inflow_and_outflow(self):
        """
        Trường hợp 1 (Luồng bình thường):
        - Nhận 2.0 ETH từ bên ngoài.
        - Chuyển 0.5 ETH ra ngoài, tốn 0.00042 ETH tiền gas.
        - Kiểm tra dòng tiền vào, dòng tiền ra và số dư cuối kỳ.
        """
        normal_txs = [
            {
                "hash": "0xaaa1",
                "timeStamp": str(self.now_ts - 50 * 86400),
                "from": "0x1111111111111111111111111111111111111111",
                "to": self.target_address,
                "value": str(2 * WEI_IN_ETH),
                "gasUsed": "21000",
                "gasPrice": str(20 * 10**9),
                "isError": "0",
                "txreceipt_status": "1",
            },
            {
                "hash": "0xaaa2",
                "timeStamp": str(self.now_ts - 20 * 86400),
                "from": self.target_address.lower(),
                "to": "0x2222222222222222222222222222222222222222",
                "value": str(int(0.5 * WEI_IN_ETH)),
                "gasUsed": "21000",
                "gasPrice": str(20 * 10**9),  # 0.00042 ETH
                "isError": "0",
                "txreceipt_status": "1",
            },
        ]
        internal_txs = []
        current_bal = 1.49958  # 2.0 - 0.50042

        records, summary = parse_and_process_transactions(
            self.target_address, normal_txs, internal_txs, 90, current_bal
        )

        self.assertEqual(len(records), 2)
        self.assertAlmostEqual(summary["total_inflow"], 2.0, places=5)
        self.assertAlmostEqual(summary["total_outflow"], 0.50042, places=5)
        self.assertAlmostEqual(summary["net_cash_flow"], 1.49958, places=5)
        self.assertAlmostEqual(summary["ending_balance"], current_bal, places=5)

    def test_02_edge_cases_failed_tx_and_self_transfer(self):
        """
        Trường hợp 2 (Trường hợp biên):
        - Giao dịch gửi tiền bị Revert (isError = 1): Value không bị trừ, phí gas vẫn bị trừ (R4).
        - Giao dịch Self-transfer: Value tự triệt tiêu về 0, chỉ tính phí gas vào outflow (R7).
        """
        normal_txs = [
            # Failed tx: gửi 5 ETH nhưng hỏng, mất 0.001 ETH gas
            {
                "hash": "0xbbb1",
                "timeStamp": str(self.now_ts - 40 * 86400),
                "from": self.target_address,
                "to": "0x3333333333333333333333333333333333333333",
                "value": str(5 * WEI_IN_ETH),
                "gasUsed": "50000",
                "gasPrice": str(20 * 10**9),  # 0.001 ETH
                "isError": "1",
                "txreceipt_status": "0",
            },
            # Self-transfer: gửi 0 ETH cho chính mình, mất 0.00042 ETH gas
            {
                "hash": "0xbbb2",
                "timeStamp": str(self.now_ts - 10 * 86400),
                "from": self.target_address.lower(),
                "to": self.target_address.upper(),  # Test case-insensitivity R10
                "value": "0",
                "gasUsed": "21000",
                "gasPrice": str(20 * 10**9),
                "isError": "0",
                "txreceipt_status": "1",
            },
        ]
        internal_txs = []
        current_bal = 10.0

        records, summary = parse_and_process_transactions(
            self.target_address, normal_txs, internal_txs, 90, current_bal
        )

        self.assertEqual(len(records), 2)
        # R4: Không trừ 5 ETH, chỉ trừ 0.001 ETH
        self.assertEqual(records[0]["type"], "OUT_FAILED")
        self.assertAlmostEqual(records[0]["outflow"], 0.001, places=6)

        # R7: Self transfer chỉ tốn gas
        self.assertEqual(records[1]["type"], "SELF_TRANSFER")
        self.assertAlmostEqual(records[1]["outflow"], 0.00042, places=6)

        expected_outflow = 0.001 + 0.00042
        self.assertAlmostEqual(summary["total_outflow"], expected_outflow, places=6)

    def test_03_fraud_adversarial_address_poisoning_and_dust_attack(self):
        """
        Trường hợp 3 (Trường hợp gian lận - Quy chuẩn AGENTS.md):
        Tấn công đầu độc lịch sử ví (Address Poisoning Attack):
        Kẻ tấn công tạo một địa chỉ Vanity giả mạo (có 4 ký tự đầu và 4 ký tự cuối giống ví người dùng)
        gửi giao dịch 0 ETH (hoặc 1 wei cực nhỏ) vào ví để làm ô nhiễm lịch sử giao dịch, nhằm lừa người dùng
        copy nhầm địa chỉ kẻ tấn công khi thực hiện các giao dịch chuyển tiền tương lai.
        Hệ thống phân tích phải:
        - Ghi nhận đúng giá trị 0 ETH (hoặc dust wei), không làm sai lệch số dư.
        - Không để xảy ra lỗi chia cho 0 hoặc lỗi tràn số.
        - Không ghi nhận phí gas của kẻ tấn công vào dòng tiền của ví mục tiêu (vì kẻ tấn công trả phí).
        """
        fake_vanity_attacker = "0x6f699999999999999999999999999999498d1F14"
        normal_txs = [
            {
                "hash": "0xpoison001",
                "timeStamp": str(self.now_ts - 5 * 86400),
                "from": fake_vanity_attacker,
                "to": self.target_address,
                "value": "0",  # Zero-value attack
                "gasUsed": "21000",
                "gasPrice": str(50 * 10**9),  # Kẻ tấn công chi trả gas cao
                "isError": "0",
                "txreceipt_status": "1",
            },
            {
                "hash": "0xdust002",
                "timeStamp": str(self.now_ts - 2 * 86400),
                "from": fake_vanity_attacker,
                "to": self.target_address,
                "value": "1",  # 1 wei dust
                "gasUsed": "21000",
                "gasPrice": str(20 * 10**9),
                "isError": "0",
                "txreceipt_status": "1",
            }
        ]
        internal_txs = []
        current_bal = 1.0

        records, summary = parse_and_process_transactions(
            self.target_address, normal_txs, internal_txs, 90, current_bal
        )

        self.assertEqual(len(records), 2)
        # Phí gas của kẻ tấn công KHÔNG được tính vào outflow của ví
        self.assertEqual(summary["total_outflow"], 0.0)
        # Dòng tiền vào chỉ tăng 1 wei = 1e-18 ETH (gần xấp xỉ 0)
        self.assertAlmostEqual(summary["total_inflow"], 1e-18, places=15)
        # Báo cáo kế toán bảo toàn tính trung thực, không bị kẻ gian thao túng
        self.assertAlmostEqual(summary["ending_balance"], current_bal, places=6)


if __name__ == "__main__":
    unittest.main()
