# SPEC — Công cụ Phân tích Dòng tiền Ví On-Chain (Lab 5 & Lab 6)

## 1. Mục đích
Xây dựng một công cụ bằng Python nhận vào một địa chỉ ví Ethereum, tự động truy xuất dữ liệu từ blockchain thông qua Etherscan API để phân tích, tổng hợp dòng tiền vào (Inflow), dòng tiền ra (Outflow) và biến động số dư của ví đó trong 90 ngày gần nhất, xuất ra bảng dữ liệu thống kê, các chỉ số tài chính tổng hợp và biểu đồ số dư theo thời gian phục vụ chuyên viên phân tích nghiệp vụ (BA), chuyên viên tuân thủ phòng chống rửa tiền (AML/KYC) và kế toán tài sản số.

---

## 2. Đầu vào
- **Địa chỉ ví mục tiêu (`target_address`):** Chuỗi ký tự độ dài đúng 42 ký tự, bắt đầu bằng `0x`, tuân thủ định dạng Hexadecimal (chuẩn EIP-55 hoặc lowercase).
- **Khóa xác thực API (`ETHERSCAN_API_KEY`):** Chuỗi ký tự bí mật đọc từ biến môi trường của hệ điều hành (`os.environ.get("ETHERSCAN_API_KEY")`), tuyệt đối không hardcode trong mã nguồn theo quy ước `AGENTS.md`.
- **Khoảng thời gian phân tích (`analysis_days`):** Số nguyên dương đại diện cho số ngày tính lùi từ thời điểm chạy báo cáo. Giá trị mặc định: `90`.
- **Mạng blockchain (`network`):** Mặc định là Ethereum Mainnet (`https://api.etherscan.io/api`), có tùy chọn cấu hình Sepolia Testnet qua tham số.

---

## 3. Quy tắc nghiệp vụ

### 3.1. Các quy tắc cơ bản (Core Rules)
- **R1 (Xác định Dòng tiền vào - Inflow):** Giao dịch thành công có trường `to` trùng khớp với `target_address` (không phân biệt chữ hoa/thường) được ghi nhận là DÒNG TIỀN VÀO. Giá trị dòng tiền vào bằng `Value` của giao dịch.
- **R2 (Xác định Dòng tiền ra - Outflow):** Giao dịch có trường `from` trùng khớp với `target_address` (không phân biệt chữ hoa/thường) được ghi nhận là DÒNG TIỀN RA.
- **R3 (Tổng tiền thực trừ khi chuyển đi):** Với giao dịch đi ra thành công, tổng số tiền thực tế bị trừ khỏi ví được tính bằng:
  $$\text{Outflow Amount} = \text{Value} + \text{Transaction Fee}$$
  Trong đó:
  $$\text{Transaction Fee} = \text{gasUsed} \times \text{gasPrice}$$
- **R4 (Xử lý Giao dịch thất bại - Failed Transactions):**
  - Nếu giao dịch có trạng thái lỗi (`isError == "1"` hoặc `txreceipt_status == "0"`):
    - *Trường hợp ví là người gửi (`from == target_address`):* Số tiền chuyển `Value` được mạng hoàn lại (không bị trừ), nhưng toàn bộ chi phí gas đã tiêu hao vẫn bị trừ vĩnh viễn khỏi ví. Do đó, ghi nhận dòng tiền ra bằng đúng `Transaction Fee` ($\text{Outflow} = \text{Transaction Fee}$, $\text{Value} = 0$).
    - *Trường hợp ví là người nhận (`to == target_address`):* Giao dịch không hoàn tất, ví không nhận được tiền và không mất phí gas $\rightarrow$ Bỏ qua, không ghi nhận vào dòng tiền.
- **R5 (Chuẩn hóa đơn vị đo lường):** Toàn bộ dữ liệu số tiền (`Value`, `Transaction Fee`) trả về từ API ở đơn vị nhỏ nhất là `wei`. Chương trình bắt buộc phải chia cho $10^{18}$ để chuyển đổi sang đơn vị `ETH` trước khi đưa vào tính toán số dư và hiển thị theo quy ước `AGENTS.md`.
- **R6 (Trật tự thời gian):** Toàn bộ danh sách giao dịch phải được sắp xếp theo mốc thời gian (`timeStamp`) tăng dần đơn điệu từ quá khứ đến hiện tại để đảm bảo tính toán số dư lũy kế chính xác.

### 3.2. Các quy tắc nghiệp vụ mở rộng (Advanced Rules - Chuẩn BA)
- **R7 (Xử lý giao dịch tự chuyển cho chính mình - Self-Transfer):**
  - Khi một giao dịch có cả `from` và `to` đều trùng với `target_address` (thao tác thường gặp khi hủy lệnh kẹt hoặc kiểm tra ví):
  - Giá trị chuyển nhượng danh nghĩa `Value` tự triệt tiêu về 0 đối với số dư ròng của ví.
  - Ví vẫn phải trả chi phí gas mạng $\rightarrow$ Ghi nhận DÒNG TIỀN RA bằng đúng `Transaction Fee`. Phân loại giao dịch này dưới nhãn `SELF_TRANSFER` để tránh tính đúp (double-counting) doanh thu/chi phí danh nghĩa trong kế toán.
- **R8 (Xác định Số dư mở kỳ và Số dư lũy kế - Historical Baseline):**
  - Biểu đồ số dư không được giả định số dư ban đầu tại mốc 90 ngày trước bằng 0 (vì có thể dẫn tới số dư âm phi lý nếu ví tiêu tiền tích lũy từ trước).
  - Thuật toán xác định số dư:
    1. Lấy số dư hiện tại của ví ($\text{Balance}_{\text{current}}$) thông qua endpoint `account.balance` tại thời điểm chạy.
    2. Tính ngược lại số dư mở kỳ tại thời điểm bắt đầu 90 ngày ($\text{Balance}_{\text{start}}$):
       $$\text{Balance}_{\text{start}} = \text{Balance}_{\text{current}} - \sum \text{Inflow} + \sum \text{Outflow}$$
    3. Tính số dư lũy kế sau mỗi giao dịch $i$:
       $$\text{Balance}_i = \text{Balance}_{i-1} + \text{Inflow}_i - \text{Outflow}_i$$
- **R9 (Truy xuất Giao dịch nội bộ - Internal Transactions):**
  - Khi ví nhận ETH từ tương tác hợp đồng thông minh (như nhận tiền từ sàn DEX, rút ETH từ két tiết kiệm `TimeLockVault`, giải ngân từ hợp đồng ký quỹ), giao dịch này nằm ở danh mục giao dịch nội bộ.
  - Công cụ phải gọi đồng thời endpoint `txlist` (giao dịch thông thường) và `txlistinternal` (giao dịch nội bộ), hợp nhất hai luồng dữ liệu trước khi phân tích để tránh thất thoát số liệu.
- **R10 (Chuẩn hóa so sánh chuỗi địa chỉ):**
  - Khi so sánh các trường `from`, `to` với `target_address`, bắt buộc phải chuyển toàn bộ về dạng chữ thường (`.lower()`) để loại bỏ sự khác biệt giữa chuẩn chữ hoa EIP-55 Checksum và chữ thường.

---

## 4. Đầu ra
1. **Bảng dữ liệu dòng tiền chi tiết (Dạng bảng Text Console hoặc DataFrame):**
   - Các cột bắt buộc: `Mã giao dịch (TxHash)`, `Thời gian (YYYY-MM-DD HH:MM:SS)`, `Loại dòng tiền (IN / OUT / SELF)`, `Giá trị chuyển (ETH)`, `Phí gas (ETH)`, `Tổng biến động (ETH)`, `Số dư lũy kế (ETH)`.
2. **Ba chỉ số tài chính tổng hợp (Executive Summary):**
   - **Tổng tiền vào (Total Inflow):** Tổng số ETH thực nhận trong 90 ngày.
   - **Tổng tiền ra (Total Outflow):** Tổng số ETH thực chuyển đi kèm toàn bộ chi phí gas tiêu thụ.
   - **Dòng tiền ròng trong kỳ (Net Cash Flow):** $\text{Total Inflow} - \text{Total Outflow}$.
   - **Số dư đầu kỳ & Số dư cuối kỳ:** Giúp đối chiếu khớp 100% với số dư on-chain thực tế.
3. **Biểu đồ trực quan hóa số dư theo thời gian (Line Chart):**
   - Trục hoành (X): Mốc thời gian (Thời điểm phát sinh giao dịch trong 90 ngày).
   - Trục tung (Y): Số dư khả dụng (ETH).
   - Điểm đánh dấu (Markers): Đánh dấu các mốc biến động lớn (Inflow lớn đánh dấu Xanh, Outflow lớn đánh dấu Đỏ).
   - Tệp biểu đồ lưu dưới định dạng PNG: `cashflow_chart.png`.

---

## 5. Trường hợp ngoại lệ & Kịch bản biên
- **Ngoại lệ 1 (Ví không có giao dịch trong 90 ngày):**
  - Nếu API trả về danh sách rỗng (`result: []`):
  - In thông báo rõ ràng: `"Vi khong co giao dich trong 90 ngay qua"`.
  - Vẫn hiển thị số dư hiện tại của ví, vẽ biểu đồ đường nằm ngang phẳng bằng đúng số dư đó, không làm sập (crash) chương trình.
- **Ngoại lệ 2 (Khóa API không hợp lệ hoặc thiếu biến môi trường):**
  - Nếu không tìm thấy `ETHERSCAN_API_KEY` trong biến môi trường hoặc API trả về lỗi xác thực (`status: "0"`, `message: "NOTOK"`):
  - In thông báo hướng dẫn: `"Loi: Khong tim thay ETHERSCAN_API_KEY hop le. Vui long kiem tra bien moi truong."` và kết thúc chương trình có kiểm soát (exit code 1).
- **Ngoại lệ 3 (Ví có trên 10.000 giao dịch - Phân trang dữ liệu):**
  - Etherscan giới hạn tối đa 10.000 bản ghi trên mỗi lần gọi.
  - Nếu số lượng bản ghi trả về đạt ngưỡng 10.000, chương trình phải tự động lấy khối cuối cùng của đợt dữ liệu đó làm `startblock` cho lần gọi tiếp theo để thu thập đầy đủ toàn bộ giao dịch trong kỳ.
- **Ngoại lệ 4 (Vượt hạn mức tần suất gọi - API Rate Limiting):**
  - Etherscan gói miễn phí giới hạn tối đa 5 requests/giây.
  - Khi thực hiện nhiều truy vấn liên tiếp (như lấy số dư, lấy txlist, lấy internal tx, duyệt nhiều trang), chương trình phải cài đặt thời gian chờ tối thiểu $0.25$ giây giữa các request (`time.sleep(0.25)`) để tránh bị trả về lỗi HTTP 429 hoặc `Max rate limit reached`.
- **Ngoại lệ 5 (Định dạng địa chỉ đầu vào không hợp lệ):**
  - Nếu địa chỉ không đúng 42 ký tự, không bắt đầu bằng `0x`, hoặc chứa ký tự ngoài hệ hex:
  - Báo lỗi ngay lập tức tại tầng nhập liệu: `"Dia chi vi khong dung dinh dang EVM (yeu cau 42 ky tu bat dau bang 0x)"`.

---

## 6. Ngoài phạm vi (Out of Scope)
- Không phân tích các giao dịch token chuẩn ERC-20, NFT (ERC-721/1155); phiên bản này chỉ tập trung vào đồng tiền gốc Native ETH.
- Không quy đổi tự động ra tiền định danh (VND hoặc USD) để tránh phụ thuộc vào API giá oracle bên thứ ba.
- Không hỗ trợ truy vết các giao dịch xuyên chuỗi (Cross-chain Bridge) sang mạng Layer 2 hoặc chuỗi khối khác.
