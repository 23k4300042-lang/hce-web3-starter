"""
scripts/wallet_analyzer.py
Phần mềm Phân tích Dòng tiền Ví On-Chain (Ethereum / Sepolia)
Học phần: Tiền điện tử & Hợp đồng thông minh (ECO2432) - Lab 6
Tuân thủ đầy đủ đặc tả SPEC.md và quy ước AGENTS.md.
"""

import os
import sys
import time
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any, Optional

# Đảm bảo mã hóa UTF-8 trên mọi nền tảng console (đặc biệt Windows cp1258/cp437)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

WEI_IN_ETH = 10**18


def check_api_status(response: requests.Response) -> Tuple[bool, str, Any]:
    """
    Quy tắc AGENTS.md: Kiểm tra trạng thái phản hồi trước khi xử lý dữ liệu.
    """
    if response.status_code != 200:
        return False, f"Lỗi HTTP {response.status_code}: {response.text}", None
    try:
        data = response.json()
    except Exception as e:
        return False, f"Không thể giải mã dữ liệu JSON từ API: {e}", None

    status = data.get("status")
    message = data.get("message")
    result = data.get("result")

    # Khi không có giao dịch, Etherscan trả về status="0", message="No transactions found"
    if status == "0":
        if "No transactions found" in str(message) or "No transactions found" in str(result):
            return True, "EMPTY_LIST", []
        # Các trường hợp lỗi xác thực API hoặc vi phạm rate limit
        return False, f"Etherscan API Error: {message} ({result})", None

    return True, "OK", result


def fetch_account_balance(
    target_address: str,
    api_key: str,
    chain_id: int = 1,
    endpoint_mode: str = "v2"
) -> float:
    """
    Lấy số dư hiện tại của ví trên chuỗi (đơn vị ETH).
    Quy tắc R5: Chia wei cho 10^18.
    """
    if endpoint_mode == "v2":
        url = "https://api.etherscan.io/v2/api"
        params = {
            "chainid": str(chain_id),
            "module": "account",
            "action": "balance",
            "address": target_address,
            "tag": "latest",
            "apikey": api_key,
        }
    else:
        base_url = "https://api.etherscan.io/api" if chain_id == 1 else "https://api-sepolia.etherscan.io/api"
        url = base_url
        params = {
            "module": "account",
            "action": "balance",
            "address": target_address,
            "tag": "latest",
            "apikey": api_key,
        }

    resp = requests.get(url, params=params, timeout=15)
    success, msg, result = check_api_status(resp)
    if not success:
        print(f"[Cảnh báo] Không thể lấy số dư trực tiếp qua API: {msg}")
        return 0.0

    try:
        balance_wei = int(result)
        return balance_wei / WEI_IN_ETH
    except (ValueError, TypeError):
        return 0.0


def fetch_transactions(
    target_address: str,
    api_key: str,
    action: str = "txlist",
    chain_id: int = 1,
    start_block: int = 0,
    endpoint_mode: str = "v2"
) -> List[Dict[str, Any]]:
    """
    Truy xuất danh sách giao dịch (txlist hoặc txlistinternal).
    Có hỗ trợ phân trang dữ liệu (Ngoại lệ 3) và điều tiết tần suất gọi (Ngoại lệ 4).
    """
    all_txs: List[Dict[str, Any]] = []
    current_start_block = start_block
    page = 1
    offset = 10000  # Ngưỡng tối đa của Etherscan

    while True:
        if endpoint_mode == "v2":
            url = "https://api.etherscan.io/v2/api"
            params = {
                "chainid": str(chain_id),
                "module": "account",
                "action": action,
                "address": target_address,
                "startblock": str(current_start_block),
                "endblock": "99999999",
                "page": str(page),
                "offset": str(offset),
                "sort": "asc",
                "apikey": api_key,
            }
        else:
            base_url = "https://api.etherscan.io/api" if chain_id == 1 else "https://api-sepolia.etherscan.io/api"
            url = base_url
            params = {
                "module": "account",
                "action": action,
                "address": target_address,
                "startblock": str(current_start_block),
                "endblock": "99999999",
                "page": str(page),
                "offset": str(offset),
                "sort": "asc",
                "apikey": api_key,
            }

        # Điều tiết tốc độ gọi API tối đa 4-5 req/giây (Ngoại lệ 4)
        time.sleep(0.25)

        try:
            resp = requests.get(url, params=params, timeout=20)
        except requests.RequestException as e:
            print(f"[Lỗi kết nối] Gặp sự cố mạng khi gọi {action}: {e}")
            break

        success, msg, result = check_api_status(resp)
        if not success:
            if msg == "EMPTY_LIST":
                break
            print(f"[Lỗi API] {action}: {msg}")
            break

        if not isinstance(result, list) or len(result) == 0:
            break

        all_txs.extend(result)

        # Nếu đạt 10.000 bản ghi thì phân trang tiếp
        if len(result) == offset:
            last_block = int(result[-1].get("blockNumber", current_start_block))
            current_start_block = last_block + 1
            page += 1
        else:
            break

    return all_txs


def parse_and_process_transactions(
    target_address: str,
    normal_txs: List[Dict[str, Any]],
    internal_txs: List[Dict[str, Any]],
    analysis_days: int,
    current_balance_eth: float
) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """
    Thực thi toàn bộ các quy tắc nghiệp vụ từ SPEC.md:
    R1 (Inflow), R2 (Outflow), R3 (Fee addition), R4 (Failed tx gas accounting),
    R5 (wei -> ETH), R6 (Timestamp sorting), R7 (Self-transfer),
    R8 (Opening balance baseline calculation), R9 (Internal tx merge), R10 (Case-insensitive).
    """
    target_addr_lower = target_address.lower()
    now_ts = int(datetime.now(timezone.utc).timestamp())
    cutoff_ts = now_ts - (analysis_days * 86400)

    processed_records: List[Dict[str, Any]] = []

    # 1. Xử lý Giao dịch thông thường (normal_txs)
    for tx in normal_txs:
        ts = int(tx.get("timeStamp", 0))
        if ts < cutoff_ts:
            continue

        tx_hash = tx.get("hash", "")
        from_addr = str(tx.get("from", "")).lower()
        to_addr = str(tx.get("to", "")).lower()

        # Kiểm tra trạng thái lỗi (R4)
        is_error = tx.get("isError") == "1" or tx.get("txreceipt_status") == "0"

        # Tính gas fee
        gas_used = int(tx.get("gasUsed", 0))
        gas_price = int(tx.get("gasPrice", 0))
        gas_fee_eth = (gas_used * gas_price) / WEI_IN_ETH

        raw_value = int(tx.get("value", 0))
        value_eth = raw_value / WEI_IN_ETH

        # Nhận diện luồng tiền
        if from_addr == target_addr_lower and to_addr == target_addr_lower:
            # R7: Self-transfer
            tx_type = "SELF_TRANSFER"
            inflow = 0.0
            outflow = gas_fee_eth
            net_delta = -gas_fee_eth
        elif from_addr == target_addr_lower:
            # R2 & R3: Outflow
            if is_error:
                # R4: Thất bại, Value hoàn lại, vẫn mất phí gas
                tx_type = "OUT_FAILED"
                inflow = 0.0
                outflow = gas_fee_eth
                net_delta = -gas_fee_eth
            else:
                tx_type = "OUT"
                inflow = 0.0
                outflow = value_eth + gas_fee_eth
                net_delta = -(value_eth + gas_fee_eth)
        elif to_addr == target_addr_lower:
            # R1: Inflow
            if is_error:
                # Giao dịch nhận tiền thất bại -> không nhận được tiền, không mất phí
                continue
            tx_type = "IN"
            inflow = value_eth
            outflow = 0.0
            net_delta = value_eth
        else:
            continue

        processed_records.append({
            "hash": tx_hash,
            "timestamp": ts,
            "datetime": datetime.fromtimestamp(ts, tz=timezone.utc),
            "type": tx_type,
            "value_eth": value_eth,
            "fee_eth": gas_fee_eth,
            "inflow": inflow,
            "outflow": outflow,
            "net_delta": net_delta,
            "is_internal": False,
        })

    # 2. Xử lý Giao dịch nội bộ (R9: internal_txs)
    # Loại bỏ trường hợp trùng hash với giao dịch thông thường nếu đã tính value
    seen_hashes = {r["hash"] for r in processed_records if r["type"] == "IN"}

    for tx in internal_txs:
        ts = int(tx.get("timeStamp", 0))
        if ts < cutoff_ts:
            continue

        tx_hash = tx.get("hash", "")
        from_addr = str(tx.get("from", "")).lower()
        to_addr = str(tx.get("to", "")).lower()
        is_error = tx.get("isError") == "1"

        if is_error:
            continue

        raw_value = int(tx.get("value", 0))
        value_eth = raw_value / WEI_IN_ETH

        if to_addr == target_addr_lower and from_addr != target_addr_lower:
            # Nhận tiền từ contract nội bộ
            if tx_hash in seen_hashes and value_eth == 0:
                continue

            processed_records.append({
                "hash": tx_hash,
                "timestamp": ts,
                "datetime": datetime.fromtimestamp(ts, tz=timezone.utc),
                "type": "IN_INTERNAL",
                "value_eth": value_eth,
                "fee_eth": 0.0,  # Người nhận nội bộ không phải trả phí khởi tạo
                "inflow": value_eth,
                "outflow": 0.0,
                "net_delta": value_eth,
                "is_internal": True,
            })

    # R6: Sắp xếp theo timestamp tăng dần đơn điệu
    processed_records.sort(key=lambda x: x["timestamp"])

    # Tính tổng hợp
    total_inflow = sum(r["inflow"] for r in processed_records)
    total_outflow = sum(r["outflow"] for r in processed_records)
    net_cash_flow = total_inflow - total_outflow

    # R8: Tính ngược lại số dư mở kỳ (Opening Balance Baseline)
    # Balance_current = Balance_start + sum(inflow) - sum(outflow)
    # -> Balance_start = Balance_current - sum(inflow) + sum(outflow)
    opening_balance = current_balance_eth - total_inflow + total_outflow
    if opening_balance < 0:
        # Trong trường hợp không lấy được current balance chính xác hoặc làm tròn
        opening_balance = max(0.0, opening_balance)

    # Tính số dư lũy kế từng bước
    running_balance = opening_balance
    for r in processed_records:
        running_balance += r["net_delta"]
        r["cumulative_balance"] = running_balance

    summary_metrics = {
        "opening_balance": opening_balance,
        "ending_balance": running_balance,
        "current_balance_onchain": current_balance_eth,
        "total_inflow": total_inflow,
        "total_outflow": total_outflow,
        "net_cash_flow": net_cash_flow,
        "tx_count": len(processed_records),
    }

    return processed_records, summary_metrics


def render_ascii_report(
    target_address: str,
    records: List[Dict[str, Any]],
    summary: Dict[str, float],
    analysis_days: int
) -> None:
    """
    In bảng báo cáo phân tích dòng tiền ra màn hình Console.
    """
    print("\n" + "=" * 90)
    print(" BÁO CÁO PHÂN TÍCH DÒNG TIỀN VÍ ON-CHAIN (LAB 6 — ECO2432)")
    print("=" * 90)
    print(f"Địa chỉ ví mục tiêu  : {target_address}")
    print(f"Thời gian phân tích  : {analysis_days} ngày gần nhất (tính từ thời điểm chạy)")
    print(f"Số lượng giao dịch   : {summary['tx_count']} giao dịch")
    print("-" * 90)
    print("CHỈ SỐ TÀI CHÍNH TỔNG HỢP (EXECUTIVE SUMMARY):")
    print(f" - Số dư đầu kỳ (Opening Balance) : {summary['opening_balance']:>14.6f} ETH")
    print(f" - Tổng tiền nạp (Total Inflow)   : {summary['total_inflow']:>14.6f} ETH")
    print(f" - Tổng tiền chi (Total Outflow)  : {summary['total_outflow']:>14.6f} ETH (Gồm chuyển tiền + Phí gas)")
    print(f" - Dòng tiền thuần (Net Cash Flow): {summary['net_cash_flow']:>+14.6f} ETH")
    print(f" - Số dư cuối kỳ (Ending Balance) : {summary['ending_balance']:>14.6f} ETH")
    print(f" - Số dư đối chiếu On-Chain       : {summary['current_balance_onchain']:>14.6f} ETH")
    print("=" * 90)

    if not records:
        print("\n[Thông báo]: Vi khong co giao dich trong 90 ngay qua (Ngoại lệ 1).\n")
        return

    print("\nBẢNG GIAO DỊCH CHI TIẾT:")
    header = (
        f"{'Mã TxHash (Rút gọn)':<18} | {'Thời gian (UTC)':<19} | {'Loại':<12} | "
        f"{'Giá trị (ETH)':<14} | {'Phí Gas (ETH)':<14} | {'Số dư lũy kế':<14}"
    )
    print(header)
    print("-" * len(header))

    # In tối đa 15 dòng đầu và 5 dòng cuối nếu danh sách quá dài
    display_records = records if len(records) <= 25 else records[:15] + [{"_skip": True}] + records[-5:]

    for r in display_records:
        if r.get("_skip"):
            print(f"{'... (đã ẩn ' + str(len(records) - 20) + ' giao dịch ở giữa) ...':^100}")
            continue

        tx_short = r["hash"][:8] + "..." + r["hash"][-6:] if r["hash"] else "INTERNAL_TX"
        dt_str = r["datetime"].strftime("%Y-%m-%d %H:%M:%S")
        val_str = f"{r['value_eth']:.6f}"
        fee_str = f"{r['fee_eth']:.6f}"
        bal_str = f"{r['cumulative_balance']:.6f}"
        print(f"{tx_short:<18} | {dt_str:<19} | {r['type']:<12} | {val_str:>14} | {fee_str:>14} | {bal_str:>14}")

    print("-" * len(header))


def plot_cashflow_chart(
    target_address: str,
    records: List[Dict[str, Any]],
    summary: Dict[str, float],
    output_path: str = "cashflow_chart.png"
) -> str:
    """
    Vẽ biểu đồ biến động số dư theo thời gian bằng matplotlib.
    Tuân thủ quy chuẩn thẩm mỹ: nền tối thanh lịch, đường nét mượt mà,
    đánh dấu Inflow (Xanh ngọc lá) và Outflow (Đỏ san hô).
    """
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)

    # Thiết lập giao diện màu sắc hiện đại
    fig.patch.set_facecolor("#0f172a")  # Slate 900
    ax.set_facecolor("#1e293b")         # Slate 800

    if not records:
        # Trường hợp ví không có giao dịch: Vẽ đường thẳng số dư hiện tại
        now = datetime.now(timezone.utc)
        times = [datetime.fromtimestamp(now.timestamp() - 90 * 86400, tz=timezone.utc), now]
        balances = [summary["current_balance_onchain"], summary["current_balance_onchain"]]
        ax.plot(times, balances, color="#38bdf8", linewidth=2.5, linestyle="--", label="Số dư không đổi")
    else:
        # Xây dựng chuỗi dữ liệu thời gian và số dư
        # Điểm bắt đầu tại thời điểm trước giao dịch đầu tiên 1 giây
        start_dt = datetime.fromtimestamp(records[0]["timestamp"] - 3600, tz=timezone.utc)
        times = [start_dt] + [r["datetime"] for r in records]
        balances = [summary["opening_balance"]] + [r["cumulative_balance"] for r in records]

        # Vẽ đường số dư chính
        ax.step(times, balances, where="post", color="#38bdf8", linewidth=2.5, label="Số dư lũy kế (ETH)")
        ax.fill_between(times, balances, step="post", color="#38bdf8", alpha=0.15)

        # Đánh dấu các mốc biến động
        inflow_times = [r["datetime"] for r in records if "IN" in r["type"] and r["inflow"] > 0]
        inflow_bals = [r["cumulative_balance"] for r in records if "IN" in r["type"] and r["inflow"] > 0]

        outflow_times = [r["datetime"] for r in records if "OUT" in r["type"]]
        outflow_bals = [r["cumulative_balance"] for r in records if "OUT" in r["type"]]

        if inflow_times:
            ax.scatter(inflow_times, inflow_bals, color="#10b981", s=60, zorder=5, label="Dòng tiền vào (Inflow)", edgecolors="#ffffff", linewidths=1.2)
        if outflow_times:
            ax.scatter(outflow_times, outflow_bals, color="#ef4444", s=50, zorder=5, label="Dòng tiền ra (Outflow)", edgecolors="#ffffff", linewidths=1.2)

    # Định dạng trục
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%Y"))
    ax.tick_params(colors="#94a3b8", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#334155")

    ax.grid(True, linestyle="--", alpha=0.25, color="#64748b")
    ax.set_title(
        f"BIỂU ĐỒ BIẾN ĐỘNG SỐ DƯ VÍ ON-CHAIN (90 NGÀY GẦN NHẤT)\nVí: {target_address}",
        fontsize=12,
        fontweight="bold",
        color="#f8fafc",
        pad=15
    )
    ax.set_xlabel("Thời gian (Mốc phát sinh giao dịch)", fontsize=11, color="#cbd5e1", labelpad=10)
    ax.set_ylabel("Số dư khả dụng (ETH)", fontsize=11, color="#cbd5e1", labelpad=10)

    legend = ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0", loc="upper left", framealpha=0.9)
    plt.tight_layout()

    # Lưu biểu đồ
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    return output_path


def generate_mock_dataset(target_address: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], float]:
    """
    Bộ dữ liệu thực nghiệm tiêu chuẩn (Synthetic Realistic Dataset)
    mô phỏng trọn vẹn mọi kịch bản nghiệp vụ:
    1. Nhận tiền từ bạn học (Inflow thông thường)
    2. Rút tiền từ hợp đồng thông minh TimeLockVault (Internal Inflow - R9)
    3. Chuyển tiền ra ngoài thành công (Outflow + Fee - R3)
    4. Giao dịch chuyển tiền thất bại do cạn gas on-chain (Failed Tx Outflow - R4)
    5. Giao dịch tự chuyển tăng tốc lệnh kẹt (Self-transfer - R7)
    6. Tấn công đầu độc địa chỉ / Phishing zero-value (Adversarial case - Kịch bản gian lận)
    """
    now = int(datetime.now(timezone.utc).timestamp())
    target_lower = target_address.lower()
    peer_addr = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045".lower()
    vault_contract = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d".lower()
    attacker_addr = "0x6f69897d262d99fc705bf7549631ca1b498d0000".lower()  # Poisoning Vanity Address

    normal_txs = [
        # Tx 1: Nhận tiền ban đầu 2.5 ETH (Inflow)
        {
            "hash": "0x1111111111111111111111111111111111111111111111111111111111111111",
            "timeStamp": str(now - 75 * 86400),
            "from": peer_addr,
            "to": target_address,
            "value": str(int(2.5 * WEI_IN_ETH)),
            "gasUsed": "21000",
            "gasPrice": str(int(20 * 10**9)),  # 20 Gwei
            "isError": "0",
            "txreceipt_status": "1",
        },
        # Tx 2: Chuyển 0.8 ETH cho đối tác (Outflow)
        {
            "hash": "0x2222222222222222222222222222222222222222222222222222222222222222",
            "timeStamp": str(now - 60 * 86400),
            "from": target_address,
            "to": peer_addr,
            "value": str(int(0.8 * WEI_IN_ETH)),
            "gasUsed": "21000",
            "gasPrice": str(int(25 * 10**9)),
            "isError": "0",
            "txreceipt_status": "1",
        },
        # Tx 3: Giao dịch chuyển tiền thất bại (Failed Tx) - Value không trừ nhưng mất phí gas
        {
            "hash": "0x3333333333333333333333333333333333333333333333333333333333333333",
            "timeStamp": str(now - 45 * 86400),
            "from": target_address,
            "to": "0x000000000000000000000000000000000000dead",
            "value": str(int(10.0 * WEI_IN_ETH)),
            "gasUsed": "45000",
            "gasPrice": str(int(30 * 10**9)),
            "isError": "1",
            "txreceipt_status": "0",
        },
        # Tx 4: Giao dịch tự gửi tăng gas (Self-Transfer) - Value = 0, tốn phí gas
        {
            "hash": "0x4444444444444444444444444444444444444444444444444444444444444444",
            "timeStamp": str(now - 30 * 86400),
            "from": target_address,
            "to": target_address,
            "value": "0",
            "gasUsed": "21000",
            "gasPrice": str(int(18 * 10**9)),
            "isError": "0",
            "txreceipt_status": "1",
        },
        # Tx 5: Kẻ tấn công giả mạo chuyển 0 ETH vào ví (Address Poisoning Attack)
        {
            "hash": "0x5555555555555555555555555555555555555555555555555555555555555555",
            "timeStamp": str(now - 15 * 86400),
            "from": attacker_addr,
            "to": target_address,
            "value": "0",
            "gasUsed": "21000",
            "gasPrice": str(int(15 * 10**9)),
            "isError": "0",
            "txreceipt_status": "1",
        },
    ]

    # Giao dịch nội bộ: Rút 1.2 ETH từ hợp đồng TimeLockVault về ví
    internal_txs = [
        {
            "hash": "0x6666666666666666666666666666666666666666666666666666666666666666",
            "timeStamp": str(now - 10 * 86400),
            "from": vault_contract,
            "to": target_address,
            "value": str(int(1.2 * WEI_IN_ETH)),
            "isError": "0",
        }
    ]

    current_balance = 2.898447  # ETH thực tế on-chain
    return normal_txs, internal_txs, current_balance


def main():
    parser = argparse.ArgumentParser(description="Công cụ Phân tích Dòng tiền Ví On-Chain (Lab 6 - ECO2432)")
    parser.add_argument("--address", type=str, default="0x6f69897D262D99Fc705bF7549631ca1b498d1F14", help="Địa chỉ ví Ethereum 42 ký tự (0x...)")
    parser.add_argument("--days", type=int, default=90, help="Số ngày phân tích (Mặc định: 90)")
    parser.add_argument("--chain", type=int, default=11155111, help="Chain ID (1: Mainnet, 11155111: Sepolia)")
    parser.add_argument("--mock", action="store_true", help="Chạy chế độ thực nghiệm dữ liệu mẫu (offline verification)")
    parser.add_argument("--api-mode", type=str, choices=["v2", "v1"], default="v2", help="Phiên bản Etherscan API (v2 Multichain hoặc v1)")
    parser.add_argument("--chart", type=str, default="cashflow_chart.png", help="Đường dẫn lưu tệp biểu đồ")

    args = parser.parse_args()

    # Kiểm tra tính hợp lệ của địa chỉ ví (Ngoại lệ 5)
    addr = args.address.strip()
    if not (addr.startswith("0x") and len(addr) == 42):
        print(f"[Lỗi đầu vào]: Địa chỉ '{addr}' không đúng định dạng EVM (yêu cầu 42 ký tự bắt đầu bằng 0x)!")
        sys.exit(1)

    # Đọc API Key từ biến môi trường (AGENTS.md & Ngoại lệ 2)
    api_key = os.environ.get("ETHERSCAN_API_KEY", "").strip()

    if args.mock or not api_key:
        if not api_key:
            print("[Thông báo]: Không tìm thấy biến môi trường ETHERSCAN_API_KEY.")
            print("[Chuyển hướng]: Tự động kích hoạt chế độ THỰC NGHIỆM DỮ LIỆU CHUẨN (Mock Dataset Mode) để kiểm tra đầy đủ 6 kịch bản nghiệp vụ theo yêu cầu bài thực hành.")
        else:
            print("[Thông báo]: Chạy chế độ thực nghiệm dữ liệu chuẩn theo cờ --mock.")

        normal_txs, internal_txs, current_bal = generate_mock_dataset(addr)
    else:
        print(f"[Khởi tạo]: Đã nạp ETHERSCAN_API_KEY từ biến môi trường. Đang truy vấn Etherscan API {args.api_mode.upper()}...")
        current_bal = fetch_account_balance(addr, api_key, chain_id=args.chain, endpoint_mode=args.api_mode)
        normal_txs = fetch_transactions(addr, api_key, action="txlist", chain_id=args.chain, endpoint_mode=args.api_mode)
        internal_txs = fetch_transactions(addr, api_key, action="txlistinternal", chain_id=args.chain, endpoint_mode=args.api_mode)

    records, summary = parse_and_process_transactions(addr, normal_txs, internal_txs, args.days, current_bal)
    render_ascii_report(addr, records, summary, args.days)

    chart_file = plot_cashflow_chart(addr, records, summary, output_path=args.chart)
    print(f"\n[Thành công]: Biểu đồ số dư đã được xuất thành công ra tệp '{chart_file}'.")


if __name__ == "__main__":
    main()
