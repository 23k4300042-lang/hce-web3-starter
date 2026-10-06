# BÁO CÁO THỰC HÀNH LAB 3 — ĐỌC GIAO DỊCH VÀ HỢP ĐỒNG TRÊN ETHERSCAN
**Tệp sản phẩm:** `lab03.md` / `forensics.md`  
**Học phần:** Tiền điện tử & Hợp đồng thông minh (ECO2432)  
**Thời lượng:** 75 phút · Thực hành cá nhân  
**Mục tiêu nghề nghiệp:** Kỹ năng phân tích on-chain, tra soát dòng tiền và thẩm định rủi ro hợp đồng thông minh cho chuyên viên Tuân thủ (AML/KYC), Kế toán và Chuyên viên phân tích nghiệp vụ (BA).  
**Mã băm giao dịch phân tích (từ Lab 2):** `0x8aeff5caccd3d961b2452bde797bcde1091ce29b2a969a18d15595819491df5d`  
**Địa chỉ ví thực hiện (From):** `0x6f69897D262D99Fc705bF7549631ca1b498d1F14`  

---
 
## PHẦN 1: MỔ XẺ 10 TRƯỜNG DỮ LIỆU CỦA GIAO DỊCH ON-CHAIN

Dưới đây là bảng phân tích chi tiết 10 trường dữ liệu cốt lõi tra cứu từ trình khám phá khối (Block Explorer: Sepolia Etherscan / Blockscout) cho giao dịch thực tế của sinh viên:

| STT | Tên trường | Giá trị thực tế trên Explorer | Ý nghĩa kỹ thuật | Vì sao người làm nghiệp vụ (Kế toán / AML / BA) cần |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Status** | `Success` / `Confirmed` (Đã vào khối) | Trạng thái thực thi của giao dịch: thành công hay thất bại (`Reverted` / `Out of Gas`). | **Kế toán:** Giao dịch thất bại vẫn bị trừ phí gas mạng. Kế toán cần biết chính xác để hạch toán chi phí mà không ghi nhận tăng tài sản đích.<br>**AML:** Loại bỏ các giao dịch thất bại khỏi luồng tiền luân chuyển thực tế. |
| **2** | **Block** | `11783491` | Số thứ tự của khối trên blockchain chứa giao dịch này. | **Kiểm toán:** Xác định vị trí bất biến của giao dịch trong sổ cái.<br>**Vận hành:** Đếm số lượng xác nhận (block confirmations). Các sàn giao dịch thường yêu cầu 12–32 confirmation mới cho phép rút/nạp tiền. |
| **3** | **Timestamp** | `2026-09-26 03:11:36 UTC` *(10:11:36 Giờ VN)* | Mốc thời gian thực khi khối được xác thực và đóng gói. | **Kế toán & Thuế:** Xác định kỳ kế toán (ngày/tháng/quý), làm căn cứ lấy tỷ giá giao ngay (spot rate) quy đổi sang VND/USD để tính thuế thu nhập/thuế GTGT theo Thông tư 15/2026 và 41/2026/TT-BTC. |
| **4** | **From / To** | **From:** `0x6f69897D...1F14`<br>**To:** `[Contract 0x11f6db...2F67a Created]` | Địa chỉ ví ký gửi (From) và địa chỉ nhận hoặc hợp đồng được khởi tạo/gọi hàm (To). | **AML/KYC:** Định danh hai bên đối tác giao dịch, rà soát địa chỉ trên danh sách đen (Blacklist/Sanction) của OFAC hoặc cơ quan hành pháp.<br>**Kế toán:** Ghi nhận bên nợ / bên có. |
| **5** | **Value** | `0 ETH` *(Lệnh khởi tạo contract)* | Lượng Native ETH được chuyển giao quyền sở hữu trực tiếp giữa From và To. | **Kế toán:** Giá trị kinh tế danh nghĩa của tài sản chuyển nhượng, làm căn cứ ghi nhận nguyên giá tài sản và đối chiếu công nợ. |
| **6** | **Transaction Fee** | `0.00030095970452143 ETH` | Tổng số phí mạng thực tế trích từ ví gửi trả cho Validator/Miner. | **Kế toán:** Chi phí vận hành mạng blockchain (OPEX). Bắt buộc phải hạch toán riêng vào chi phí hoạt động của doanh nghiệp, không trừ gộp vào Value. |
| **7** | **Gas Price** | `2.55737621 Gwei`<br>*(Base: 1.057 + Priority: 1.5 Gwei)* | Đơn giá cho mỗi đơn vị gas tại thời điểm đóng khối (theo chuẩn EIP-1559). | **BA / Quản lý tài chính:** Giải thích nguyên nhân vì sao cùng một thao tác mà lúc cao điểm chi phí tốn gấp nhiều lần lúc thấp điểm, từ đó thiết kế quy trình xử lý giao dịch tự động vào khung giờ thấp điểm. |
| **8** | **Gas Limit** | `118,733` | Hạn mức gas tối đa mà ví người gửi ủy quyền cho giao dịch tiêu thụ. | **Thẩm định an toàn:** Lá chắn bảo vệ số dư ví. Đặt quá thấp dẫn đến lỗi `Out of Gas` (mất tiền phí oan). Đặt quá cao khi tương tác với hợp đồng lỗi có thể bị "rút cạn" phí. |
| **9** | **Gas Used** | `117,683`<br>*(Tỷ lệ tiêu thụ: 99.12% Gas Limit)* | Lượng đơn vị tính toán thực tế mà máy ảo Ethereum (EVM) đã tiêu thụ. | **Kế toán & Kiểm toán:** Tính toán chi phí thực tế: $\text{Fee} = \text{Gas Used} \times \text{Gas Price}$. Dấu hiệu `Gas Used == Gas Limit` trong giao dịch lỗi báo hiệu cạn kiệt gas (`Out of Gas`). |
| **10** | **Nonce** | `50` | Số thứ tự tăng dần liên tục của các giao dịch phát ra từ ví gửi (giao dịch thứ 51). | **Đối soát & Kỹ thuật:** Đảm bảo thứ tự thực thi, chống tấn công phát lại (Replay Attack). Phát hiện giao dịch bị tắc nghẽn (pending) khiến toàn bộ giao dịch sau bị treo. |

---

## PHẦN 2: ĐỌC VÀ THẨM ĐỊNH HỢP ĐỒNG THẬT TRÊN ETHEREUM MAINNET

Học phần tiến hành thẩm định hai hợp đồng Stablecoin lớn nhất thế giới trên mạng Ethereum Mainnet:
- **Hợp đồng 1 (Trực tiếp):** Tether USD (USDT) — `0xdAC17F958D2ee523a2206206994597C13D831ec7`
- **Hợp đồng 2 (Proxy EIP-1967):** USD Coin (USDC) — `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`

### 2.1. Phân biệt Bytecode và Source Code (Verified)
- **Bytecode (Mã máy):** Chuỗi ký tự thập lục phân (hex) opcode lưu trữ trực tiếp trên EVM. Máy tính đọc và thực thi được nhưng con người không thể hiểu được các điều khoản kinh tế bên trong.
- **Verified Source Code (Mã nguồn đã xác thực):** Mã nguồn viết bằng ngôn ngữ bậc cao (Solidity) do bên phát hành tải lên Etherscan. Trình biên dịch của Etherscan đã biên dịch lại độc lập và đối chiếu thấy khớp 100% từng byte với Bytecode on-chain.
- **Ý nghĩa thẩm định rủi ro:** Nếu một dự án phát hành token/DApp huy động vốn mà **không công bố Verified Source Code**, đây là tín hiệu cảnh báo đỏ (Red Flag). Rủi ro cao tồn tại mã độc, bẫy rút thanh khoản (rug pull) hoặc cửa sau (backdoor).

### 2.2. Bài học cốt lõi về Proxy Contract (Mẫu EIP-1967) qua trường hợp USDC
- Khi mở địa chỉ của USDC trên Etherscan, tab `Read Contract` và `Write Contract` chỉ hiển thị các hàm quản trị proxy: `upgradeTo(address)`, `changeAdmin(address)`. Không hề có các hàm token như `transfer`, `balanceOf`, `totalSupply`.
- **Cơ chế hoạt động:** USDC áp dụng mô hình Proxy có thể nâng cấp. Địa chỉ `0xA0b86...` chỉ là vỏ bọc **Proxy Contract** lưu trữ trạng thái dữ liệu (State/Balances). Toàn bộ logic nghiệp vụ thực tế nằm tại một hợp đồng khác gọi là **Implementation Contract**.
- **Cách xem:** Trên Etherscan, bắt buộc phải chọn tab con **Read as Proxy** và **Write as Proxy**. Khi đó, Etherscan sẽ đọc ABI từ địa chỉ Implementation để hiển thị các hàm nghiệp vụ token.
- **Bài học cho chuyên viên thẩm định:** Mã nguồn xác thực ở địa chỉ Proxy không đại diện cho logic nghiệp vụ thực tế. Phải luôn truy ngược về địa chỉ Implementation để kiểm tra các điều khoản kinh tế thật sự.

---

## PHẦN 3: TRẢ LỜI 3 CÂU HỎI BẮT BUỘC

### Câu hỏi 1: Hợp đồng bạn xem có công bố mã nguồn đã xác thực không?
**Trả lời:**
- **Có.** Cả hai hợp đồng USDT (`0xdAC17...`) và USDC (`0xA0b86...` cùng hợp đồng Implementation của nó) đều đã được công bố mã nguồn và có tích xanh **Contract Source Code Verified** trên Etherscan.
- Việc công bố mã nguồn cho phép công chúng, kiểm toán viên độc lập và nhà đầu tư có thể đọc, rà soát và kiểm chứng tính toàn vẹn của logic tiền tệ trước khi tham gia giao dịch.

### Câu hỏi 2: Tổng cung của đồng đó là bao nhiêu? Đọc ra từ hàm nào?
**Trả lời:**
- **Tên hàm đọc:** Đọc từ hàm `totalSupply()` (thuộc dạng hàm `view`, nằm trong tab **Read Contract** đối với USDT và tab **Read as Proxy** đối với USDC).
- **Cách tính toán:**
  - Đối với **USDT:**
    - Kết quả trả về từ hàm `totalSupply()` trên Etherscan là một số nguyên lớn: `88304342264550000`.
    - Đọc tiếp hàm `decimals()` trả về giá trị là `6`.
    - Số lượng token thực tế:
      $$\text{Total Supply} = \frac{88,304,342,264,550,000}{10^6} \approx \mathbf{88.304.342.264,55 \text{ USDT}}$$
      *(Tương đương hơn 88,3 tỷ USD lưu hành).*
  - Đối với **USDC:** Tương tự, gọi hàm `totalSupply()` qua tab `Read as Proxy` và chia cho $10^6$ decimals để ra tổng lượng cung thực tế tại thời điểm tra cứu.

### Câu hỏi 3: Trong tab Write Contract (với USDC: Write as Proxy), có hàm nào cho phép một địa chỉ đặc biệt đóng băng tài khoản người khác không? Nếu có, tên hàm là gì?
**Trả lời:**
- **CÓ. Cả hai đồng ổn định giá lớn nhất thế giới đều sở hữu cơ chế đóng băng tài khoản người dùng:**
  - **Đối với Tether (USDT):**
    - Hàm đóng băng: `addBlackList(address _evilUser)`.
    - Hàm gỡ đóng băng: `removeBlackList(address _clearedUser)`.
    - Hàm tiêu hủy số dư trong tài khoản bị đóng băng: `destroyBlackFunds(address _blackListedUser)`.
    - *Quyền hạn thực hiện:* Chỉ duy nhất chủ sở hữu hợp đồng (`owner`) mới có quyền kích hoạt các hàm này.
  - **Đối với USD Coin (USDC):**
    - Hàm đóng băng: `blacklist(address _account)`.
    - Hàm gỡ đóng băng: `unBlacklist(address _account)`.
    - *Quyền hạn thực hiện:* Chỉ địa chỉ được cấp vai trò quản lý danh sách đen (`onlyBlacklister`) mới có quyền gọi.

---

## PHẦN 4: ĐÁNH GIÁ VÀ KẾT LUẬN NGHIỆP VỤ

### Ý nghĩa kinh tế và tranh luận về "Tính phi tập trung thực tế"
1. **Lầm tưởng phổ biến:** Nhiều người mới tiếp cận Web3 tin rằng tài sản mã hóa luôn phi tập trung hoàn toàn và *"không ai có quyền can thiệp vào ví của tôi"*.
2. **Thực tế thị trường:** Hai stablecoin chiếm hơn 85% thanh khoản toàn thị trường (USDT và USDC) đều là **tài sản tập trung (Centralized Tokens)**. Các tổ chức phát hành (Tether Limited và Circle Internet Financial) chịu sự điều chỉnh của luật pháp sở tại và các cơ quan quản lý tài chính quốc tế (như lệnh trừng phạt OFAC của Bộ Tài chính Hoa Kỳ).
3. **Cơ chế cưỡng chế tuân thủ:** Chức năng Blacklist là công cụ bắt buộc để các tổ chức này đóng băng tài sản liên quan đến tin tặc, tội phạm rửa tiền, khủng bố hoặc theo yêu cầu phong tỏa của tòa án.
4. **Góc nhìn thẩm định rủi ro:** Người nắm giữ USDT/USDC phải chấp nhận rủi ro đối tác tập trung (Counterparty Risk): số dư của họ có thể bị vô hiệu hóa bất kỳ lúc nào nếu địa chỉ ví bị gán nhãn rủi ro hoặc nằm trong diện điều tra.
