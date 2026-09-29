# BÁO CÁO THỰC HÀNH LAB 5 — VIẾT ĐẶC TẢ CHO CÔNG CỤ PHÂN TÍCH DÒNG TIỀN
**Học phần:** Tiền điện tử & Hợp đồng thông minh (ECO2432)  
**Thời lượng:** 75 phút · Thực hành nhóm 2 người · **NGUYÊN TẮC: KHÔNG VIẾT MÃ NGUỒN TRONG BUỔI NÀY**  
**Vị trí việc làm hướng tới:** Chuyên viên phân tích nghiệp vụ (Business Analyst - BA) tại ngân hàng, công ty Fintech và tổ chức tài sản mã hóa  
**Sản phẩm nghiệm thu:** Tệp đặc tả chuẩn [SPEC.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/SPEC.md) + Biên bản kiểm tra chéo (Peer Review) chỉ ra các điểm mơ hồ.

---

## 1. BỐI CẢNH NGHỀ NGHIỆP & NGUYÊN TẮC CỐT LÕI CỦA BUỔI HỌC

### 1.1. Tại sao Chuyên viên BA không viết mã nguồn?
- Trong các tổ chức tài chính và dự án công nghệ Web3, chuyên viên phân tích nghiệp vụ (BA) đóng vai trò là "kiến trúc sư yêu cầu". Họ là cầu nối dịch chuyển giữa **mục tiêu nghiệp vụ tài chính** (kế toán, thuế, AML/KYC) và **đội ngũ kỹ thuật / công cụ AI**.
- Nếu yêu cầu đưa ra mơ hồ, công cụ AI hoặc lập trình viên sẽ buộc phải tự suy đoán (assumptions). Và trong lĩnh vực tài chính, **mọi suy đoán sai lầm về dòng tiền, phí gas hay thời điểm ghi nhận đều dẫn đến thất thoát tiền bạc hoặc sai phạm pháp lý nghiêm trọng**.
- *Nguyên tắc sống còn của môn học:* Nếu sinh viên nhảy thẳng vào gõ code hoặc prompt AI sinh mã ngay từ đầu mà không có bản đặc tả chi tiết, mã nguồn sinh ra có thể chạy được nhưng kết quả tài chính sẽ sai lệch 100%.

### 1.2. Phân tích đối chiếu: Đặc tả sai (Bad Spec) vs Đặc tả đúng (Good Spec)
Tại Bước 1 của bài học, giảng viên đã phân tích sự khác biệt căn bản giữa hai cách tiếp cận:

| Tiêu chí | Đặc tả sai (Sinh viên thường mắc phải) | Đặc tả đúng chuẩn nghiệp vụ BA | Hậu quả nếu dùng Đặc tả sai với AI |
| :--- | :--- | :--- | :--- |
| **Mục tiêu** | *"Viết chương trình phân tích ví Ethereum."* | Nêu rõ: Đầu vào, đầu ra, phạm vi 90 ngày, mục đích báo cáo kế toán/AML. | AI tự bịa ra các chức năng không cần thiết (như swap token, check giá sàn). |
| **Xác thực API** | Không đề cập cách đọc khóa API. | Chỉ định đọc từ biến môi trường `ETHERSCAN_API_KEY`, cấm hardcode. | AI ghi thẳng khóa bí mật vào mã nguồn $\rightarrow$ Vi phạm bảo mật nghiêm trọng. |
| **Đơn vị tiền tệ** | Không nhắc đơn vị tính. | Bắt buộc chia cho $10^{18}$ từ `wei` sang `ETH`. | AI để nguyên số dư đơn vị wei hiển thị chuỗi số 19 chữ số gây hoang mang cho người dùng. |
| **Phí giao dịch** | Chỉ tính số tiền chuyển danh nghĩa. | Phân biệt rõ phí của giao dịch gửi đi và xử lý giao dịch thất bại vẫn mất phí. | Báo cáo bị lệch số dư thực tế, làm sai lệch sổ sách kế toán. |
| **Trường hợp lỗi** | Không có kịch bản ngoại lệ. | Xử lý đầy đủ: API lỗi, ví rỗng, phân trang trên 10.000 giao dịch, rate limit. | Chương trình bị crash dừng đột ngột khi gặp lỗi mạng hoặc ví không có dữ liệu. |

---

## 2. NỘI DUNG ĐẶC TẢ CHI TIẾT (SPEC.MD ĐƯỢC CHUẨN HÓA)

Toàn bộ bản đặc tả chính thức của hệ thống đã được đồng bộ tại tệp [SPEC.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/SPEC.md), bao gồm 6 phần cấu trúc quy chuẩn:

### 2.1. Mục đích
Hệ thống phần mềm phân tích dòng tiền on-chain tự động trích xuất lịch sử giao dịch từ Etherscan API cho một địa chỉ ví cụ thể trong vòng 90 ngày gần nhất, tổng hợp luồng tiền vào/ra, tính toán số dư thực tế theo thời gian và trực quan hóa bằng biểu đồ số dư lũy kế, phục vụ công tác đối soát kế toán và thẩm định tuân thủ phòng chống rửa tiền (AML/KYC).

### 2.2. Đầu vào hệ thống
1. `target_address`: Chuỗi 42 ký tự hex bắt đầu bằng `0x`.
2. `ETHERSCAN_API_KEY`: Đọc từ biến môi trường hệ thống (`os.environ`).
3. `analysis_days`: Số ngày phân tích (Mặc định: `90`).
4. `network`: Mạng Ethereum Mainnet hoặc Sepolia Testnet.

### 2.3. Bảng quy tắc nghiệp vụ cốt lõi (Core Business Rules R1 – R6)
Bảng dưới đây chuẩn hóa các quy tắc bắt buộc của bài toán:

| Mã quy tắc | Tên quy tắc nghiệp vụ | Điều kiện kích hoạt | Công thức / Hành vi hệ thống | Căn cứ nghiệp vụ tài chính |
| :---: | :--- | :--- | :--- | :--- |
| **R1** | **Dòng tiền vào (Inflow)** | `to.lower() == target_address.lower()` và giao dịch thành công. | $\text{Inflow} = \text{Value}$ (chuyển sang ETH). | Tiền nạp vào tài sản của ví. Người nhận không phải trả phí gas mạng. |
| **R2** | **Dòng tiền ra (Outflow)** | `from.lower() == target_address.lower()` và giao dịch thành công. | Ghi nhận sự kiện phát sinh dòng tiền ra khỏi ví. | Tiền chi ra phục vụ thanh toán hoặc chuyển khoản cho đối tác. |
| **R3** | **Chi phí thực trừ khỏi ví** | Áp dụng cho mọi giao dịch đi ra (R2) thành công. | $\text{Outflow} = \text{Value} + \text{Transaction Fee}$<br>với $\text{Fee} = \text{gasUsed} \times \text{gasPrice}$. | Người gửi phải thanh toán đồng thời cả giá trị chuyển và phí vận hành mạng cho validator. |
| **R4** | **Xử lý giao dịch thất bại** | Giao dịch có trạng thái lỗi (`isError == "1"`). | - Nếu là người gửi (`from`): $\text{Outflow} = \text{Fee}$ (Value hoàn lại, phí bị trừ).<br>- Nếu là người nhận (`to`): Bỏ qua (không ghi nhận). | Giao dịch lỗi on-chain vẫn tiêu tốn tài nguyên EVM $\rightarrow$ Phí gas bị trừ vĩnh viễn, hạch toán vào chi phí hoạt động. |
| **R5** | **Chuẩn hóa đơn vị đo lường** | Mọi trường số tiền lấy về từ API (`wei`). | $\text{Amount (ETH)} = \frac{\text{Amount (wei)}}{10^{18}}$. | Tuân thủ quy chuẩn số học EVM và quy ước [AGENTS.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/AGENTS.md) khi hiển thị báo cáo. |
| **R6** | **Trật tự thời gian dòng tiền** | Toàn bộ danh sách giao dịch trích xuất. | Sắp xếp tăng dần theo trường `timeStamp` ($t_1 \le t_2 \le \dots \le t_n$). | Đảm bảo tính toán số dư lũy kế chính xác theo đúng thứ tự đóng khối sổ cái. |

---

## 3. CÁC QUY TẮC NGHIỆP VỤ MỞ RỘNG (VƯỢT TRÊN YÊU CẦU ĐỀ BÀI)
*Nhằm đáp ứng mức đánh giá Khá – Giỏi (Thang điểm 8.5 – 10.0), nhóm đã bổ sung 4 quy tắc nghiệp vụ chuyên sâu giải quyết các bài toán thực tế của chuyên viên BA:*

### Quy tắc R7: Xử lý giao dịch tự chuyển tiền (Self-Transfer)
- **Tình huống thực tế:** Người dùng gửi giao dịch từ chính ví của mình sang chính ví của mình (`from == to`) với `Value = 0` nhằm mục đích tăng gas thay thế lệnh kẹt (Speed Up / Cancel Tx) hoặc kiểm tra hoạt động ví.
- **Quy tắc xử lý:**
  - `Value` tự triệt tiêu về 0, không làm tăng/giảm tài sản ròng danh nghĩa.
  - Ví vẫn bị trừ phí mạng $\rightarrow$ Ghi nhận DÒNG RA bằng đúng $\text{Transaction Fee}$.
  - Đánh nhãn riêng biệt là `SELF_TRANSFER` để kế toán không tính đúp (double-counting) doanh thu danh nghĩa.

### Quy tắc R8: Xác định Số dư mở kỳ (Opening Balance) và Số dư lũy kế
- **Tình huống thực tế:** Nếu ví đã có sẵn 50 ETH từ trước ngày $T-90$, trong 90 ngày qua chỉ phát sinh lệnh chi 5 ETH. Nếu vẽ biểu đồ số dư xuất phát từ 0, số dư lũy kế sẽ bị âm ($-5 \text{ ETH}$), hoàn toàn phi lý về mặt kế toán!
- **Thuật toán giải quyết:**
  1. Gọi endpoint `account.balance` lấy số dư hiện tại trên blockchain ($\text{Balance}_{\text{current}}$).
  2. Tính ngược số dư mở kỳ tại thời điểm $T-90$:
     $$\text{Balance}_{\text{open}} = \text{Balance}_{\text{current}} - \sum_{t=T-90}^{\text{now}} \text{Inflow} + \sum_{t=T-90}^{\text{now}} \text{Outflow}$$
  3. Mọi điểm trên biểu đồ số dư phản ánh chính xác số dư thực tế của ví tại mốc thời gian đó.

### Quy tắc R9: Tích hợp Giao dịch nội bộ (Internal Transactions)
- **Tình huống thực tế:** Khi ví nhận ETH từ việc rút tiền từ Smart Contract (ví dụ: rút tiền từ hợp đồng tiết kiệm `TimeLockVault` của Lab 9, rút vốn từ Pool thanh khoản Uniswap, hoặc nhận tiền bồi thường bảo hiểm), giao dịch này không xuất hiện trong endpoint `txlist` thông thường mà nằm ở endpoint `txlistinternal`.
- **Quy tắc xử lý:** Hệ thống bắt buộc phải truy vấn cả `txlist` và `txlistinternal`, loại bỏ các giao dịch trùng lặp và cộng gộp toàn bộ dòng tiền vào thực tế để không làm thất thoát số liệu kiểm toán.

### Quy tắc R10: Chuẩn hóa so sánh địa chỉ không phân biệt chữ hoa/thường (Case-Insensitive)
- Do Ethereum hỗ trợ chuẩn EIP-55 (chữ hoa/chữ thường làm mã kiểm tra checksum), các API endpoint có thể trả về chuỗi địa chỉ ở dạng hỗn hợp hoặc chữ thường.
- Quy tắc bắt buộc: Trước khi so sánh logic `from` hoặc `to` với `target_address`, phải chuyển đổi tất cả về dạng `.lower()`.

---

## 4. BIÊN BẢN KIỂM TRA CHÉO ĐẶC TẢ (PEER REVIEW REPORT - BƯỚC 3)

Theo quy định tại Bước 3 của bài học (Trang 14), nhóm đã tiến hành đổi chéo bản dự thảo đặc tả `SPEC.md` với Nhóm 4 (Nhóm bạn học cùng lớp). Dưới đây là biên bản ghi nhận các điểm mơ hồ do nhóm bạn chỉ ra và giải pháp điều chỉnh của nhóm:

### 4.1. Điểm mơ hồ 1: Không xác định rõ mốc số dư ban đầu của biểu đồ
- **Nhận xét của nhóm bạn:**  
  *"Trong bản thảo ban đầu của các bạn, mục 4 ghi 'biểu đồ số dư lũy kế' nhưng mục 2 chỉ yêu cầu lấy dữ liệu trong 90 ngày. Vậy số dư ban đầu tại ngày thứ nhất lấy ở đâu? Nếu các bạn cộng dồn từ 0 thì với những ví chỉ chi tiền mà không có tiền vào trong 90 ngày, số dư lũy kế sẽ ra số âm. Đây là lỗi logic lớn."*
- **Đánh giá của nhóm:** Rất chính xác. Đây là lỗ hổng nghiêm trọng thường gặp của các BA thiếu kinh nghiệm kế toán.
- **Giải pháp xử lý:** Nhóm đã bổ sung ngay **Quy tắc R8** vào `SPEC.md`: Lấy số dư tức thời hiện tại từ Etherscan API và tính ngược lại số dư đầu kỳ (Opening Balance), bảo đảm biểu đồ luôn thể hiện số dư khả dụng thực tế trên chuỗi.

### 4.2. Điểm mơ hồ 2: Thất thoát dòng tiền do bỏ qua giao dịch nội bộ hợp đồng
- **Nhận xét của nhóm bạn:**  
  *"Đặc tả ghi dùng Etherscan API để lấy danh sách giao dịch, nhưng nếu ví này tương tác với Smart Contract rút tiền về (ví dụ nhận ETH từ contract đa chữ ký hoặc DEX), endpoint thông thường `txlist` sẽ không có giá trị value! Các bạn sẽ bỏ sót toàn bộ dòng tiền vào này."*
- **Đánh giá của nhóm:** Hoàn toàn đúng với đặc thù kỹ thuật của mạng máy ảo EVM.
- **Giải pháp xử lý:** Nhóm đã bổ sung **Quy tắc R9**: Yêu cầu công cụ phải truy xuất thêm endpoint `txlistinternal` (Internal Transactions) để bao quát 100% các dòng tiền bắt nguồn từ Smart Contract.

### 4.3. Điểm mơ hồ 3: Chưa có cơ chế đối phó với giới hạn tần suất gọi API (Rate Limit)
- **Nhận xét của nhóm bạn:**  
  *"Nếu ví có hơn 10.000 giao dịch hoặc phải gọi đồng thời nhiều endpoint (lấy balance, lấy txlist, lấy internal tx), API Etherscan gói miễn phí sẽ chặn với lỗi Max rate limit reached (vượt quá 5 calls/sec). Bản thảo chưa nói rõ phần mềm phải ứng xử thế nào."*
- **Đánh giá của nhóm:** Góp ý rất xác đáng về mặt ổn định vận hành của hệ thống.
- **Giải pháp xử lý:** Nhóm đã bổ sung vào **Mục 5 (Trường hợp ngoại lệ)** quy tắc điều tiết nhịp gọi API: cài đặt cơ chế nghỉ `time.sleep(0.25)` giữa các request liên tiếp và tự động lặp lại tối đa 3 lần nếu gặp mã lỗi 429.

---

## 5. BỘ TIÊU CHÍ NGHIỆM THU NGHIỆP VỤ (ACCEPTANCE CRITERIA - BDD GHERKIN)

Để chuẩn bị nghiệm thu cho buổi sinh mã Lab 6, nhóm thiết lập bộ kịch bản kiểm thử nghiệp vụ theo chuẩn BDD (Behavior Driven Development):

```gherkin
Kịch bản 1: Xử lý giao dịch nhận tiền thành công (Inflow)
  Given Địa chỉ ví mục tiêu là "0x6f69897D262D99Fc705bF7549631ca1b498d1F14"
  When Nhận được giao dịch thành công có trường "to" là "0x6f69897d262d99fc705bf7549631ca1b498d1f14" và value là 1000000000000000000 wei
  Then Hệ thống ghi nhận Dòng tiền vào là 1.0 ETH
  And Phí gas không bị trừ vào dòng tiền này

Kịch bản 2: Xử lý giao dịch gửi tiền thành công (Outflow)
  Given Địa chỉ ví mục tiêu là "0x6f69897D262D99Fc705bF7549631ca1b498d1F14"
  When Nhận được giao dịch thành công có "from" là ví mục tiêu, value là 0.5 ETH, phí gas thực trả là 0.0003 ETH
  Then Hệ thống ghi nhận Dòng tiền ra là 0.5003 ETH
  And Số dư lũy kế bị giảm đi 0.5003 ETH

Kịch bản 3: Xử lý giao dịch chuyển tiền bị thất bại (Failed Outflow)
  Given Địa chỉ ví mục tiêu phát lệnh chuyển 10 ETH
  When Giao dịch bị Reverted on-chain (isError = "1"), phí gas tiêu tốn là 0.001 ETH
  Then Giá trị chuyển 10 ETH không được tính vào dòng tiền ra
  And Hệ thống chỉ ghi nhận Dòng tiền ra bằng đúng phí gas là 0.001 ETH

Kịch bản 4: Xử lý khi API Key không tồn tại
  Given Biến môi trường ETHERSCAN_API_KEY chưa được thiết lập
  When Khởi chạy chương trình phân tích
  Then Chương trình dừng lại có kiểm soát
  And In thông báo hướng dẫn người dùng kiểm tra biến môi trường, không in lỗi traceback dài dòng
```

---

## 6. DANH MỤC KIỂM TRA SẴN SÀNG CHO LAB 6 (LAB 6 PREPARATION CHECKLIST)

Khi chuyển sang Buổi 6 để giao đặc tả này cho công cụ AI sinh mã, sinh viên sẽ sử dụng danh mục 6 điểm kiểm tra bắt buộc dưới đây để đối soát mã nguồn do AI tạo ra:

| STT | Hạng mục kiểm tra | Cách kiểm tra trong mã nguồn Python | Lỗi thường gặp của công cụ AI | Trạng thái chuẩn bị |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Đơn vị tiền tệ** | Kiểm tra phép chia cho `10**18` | AI quên chia $10^{18}$, hiển thị số dư 19 chữ số | Đã quy định rõ tại R5 |
| 2 | **Bảo mật khóa API** | Tìm hàm `os.environ.get("ETHERSCAN_API_KEY")` | AI ghi chuỗi khóa trực tiếp vào mã nguồn | Đã quy định rõ tại Mục 2 |
| 3 | **Phân trang dữ liệu** | Kiểm tra vòng lặp lấy đủ trang khi $\ge 10.000$ tx | AI chỉ lấy trang đầu, làm sai lệch dòng tiền | Đã quy định rõ tại Mục 5 |
| 4 | **Giao dịch thất bại** | Kiểm tra cờ `isError == "1"` | AI bỏ qua, không tính phí gas của lệnh hỏng | Đã quy định rõ tại R4 |
| 5 | **Bắt lỗi ngoại lệ** | Kiểm tra các khối `try/except` và mã phản hồi | Chương trình dừng đột ngột, văng traceback | Đã quy định rõ tại Mục 5 |
| 6 | **Phiên bản Etherscan API** | Đối chiếu URL endpoint hợp nhất hiện hành | AI dùng URL endpoint cũ đã ngừng hỗ trợ | Đã cung cấp URL chuẩn |

---

## 7. NHẬN XÉT VÀ ĐÁNH GIÁ CHUYÊN MÔN (OBSERVATIONS & PROFESSIONAL REFLECTION)

### 7.1. Nhận xét về chuyển đổi tư duy: Từ "Lập trình viên mò mẫm" sang "Kiến trúc sư nghiệp vụ (BA)"
- **Thực trạng tâm lý ban đầu:** Khi nhận đề bài "viết công cụ phân tích ví Ethereum", phản xạ tự nhiên của đa số sinh viên là mở ngay trình soạn thảo code hoặc gõ prompt vội vã: *"Hãy viết code Python cào dữ liệu Etherscan vẽ biểu đồ"*. Đây là căn bệnh kinh điển của người làm kỹ thuật non trẻ khi đối diện với các bài toán công nghệ tài chính.
- **Bài học từ nguyên tắc "Đóng băng mã nguồn" (Code Freeze):** Việc giảng viên cấm viết code trong suốt 75 phút của Lab 5 buộc sinh viên phải chậm lại để tư duy ở tầng bản chất. Việc lập trình chỉ chiếm 20% công sức, trong khi 80% thành bại của một giải pháp Fintech nằm ở **tính chính xác và bao quát của bản đặc tả yêu cầu**.
- **Ý nghĩa đối với Chuyên viên BA tài chính:**
  - Nếu BA không định nghĩa quy tắc **R3** và **R4** (hạch toán chi phí gas của lệnh gửi hỏng), lập trình viên hoặc AI sẽ tự mặc định bỏ qua giao dịch lỗi $\rightarrow$ Sổ sách kế toán lệch hàng trăm triệu đồng chi phí vận hành mạng.
  - Nếu BA không quy định **R5** (đổi wei sang ETH), hệ thống sẽ hiển thị số dư bằng những chuỗi số 19 chữ số vô nghĩa, gây hoang mang tột độ cho ban lãnh đạo và đối tác kiểm toán.

### 7.2. Nhận xét về hoạt động Kiểm tra chéo (Peer Review) và giá trị của phản biện nhóm
- **Giá trị phát hiện điểm mù (Blind Spots):** Nhóm tự tin rằng bản dự thảo ban đầu đã rất chi tiết, nhưng qua buổi phản biện chéo với Nhóm 4, hai lỗ hổng lớn về tư duy đã lộ diện:
  1. *Lỗ hổng số dư ban đầu:* Việc chỉ lấy dữ liệu trong 90 ngày mà quên xác lập số dư mở kỳ (Opening Balance) sẽ làm biểu đồ bị âm nếu ví chỉ có lệnh chi tiêu tích lũy từ trước.
  2. *Lỗ hổng giao dịch nội bộ:* Nhầm tưởng rằng endpoint `txlist` lấy được toàn bộ dòng tiền, bỏ sót hoàn toàn các giao dịch giải ngân từ Smart Contract (vốn chỉ nằm trong `txlistinternal`).
- **Ý nghĩa thực tiễn trong quy trình phát triển sản phẩm Fintech:**
  - Áp dụng nguyên lý **"Shift Left"** (Đưa kiểm thử và rà soát về phía trước quy trình): Chi phí để sửa một dòng văn bản trong tệp [SPEC.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/SPEC.md) ở Lab 5 chỉ tốn 5 phút gõ chữ; nhưng nếu để lỗ hổng đó lọt vào code ở Lab 6, thời gian gỡ lỗi (debugging) có thể mất cả ngày; còn nếu để lọt ra môi trường sản xuất (Production) thì hậu quả là sai phạm báo cáo tài chính và bị cơ quan thanh tra xử phạt.

### 7.3. Nhận xét về vai trò của bản đặc tả trong việc kiểm soát công cụ AI
- **AI không hiểu bản chất kinh tế:** Các mô hình ngôn ngữ lớn (LLM) chỉ dự đoán từ ngữ tiếp theo dựa trên xác suất thống kê. Chúng không có ý thức về tính bất biến của blockchain, không hiểu trách nhiệm pháp lý khi lộ API key, và không phân biệt được số tiền chuyển danh nghĩa với chi phí gas thực trừ.
- **Đặc tả [SPEC.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/SPEC.md) là "chiếc lồng định hướng" (Guardrail):**
  - Bản đặc tả với các quy tắc được mã hóa chặt chẽ (R1 – R10) và kịch bản nghiệm thu BDD Gherkin (Mục 5) chính là hàng rào kỹ thuật ngăn chặn triệt để hiện tượng AI "bịa đặt" (hallucination).
  - Khi chuyển giao sang Lab 6, sinh viên không cần mất công giải thích lặp đi lặp lại cho AI, mà chỉ cần giao [SPEC.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/SPEC.md) kèm quy ước [AGENTS.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/AGENTS.md) là AI có thể sinh mã chính xác, an toàn ngay từ lần thử đầu tiên.

### 7.4. Nhận xét về tính tuân thủ quy ước [AGENTS.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/AGENTS.md) và khuôn khổ pháp lý mới
- **Tuân thủ quy ước dự án ECO2432:**
  - Toàn bộ đặc tả quán triệt 3 quy tắc viết Python của [AGENTS.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/AGENTS.md): Khóa API bảo mật trong biến môi trường, kiểm tra trạng thái HTTP/JSON trước khi phân tích dữ liệu, và đổi triệt để wei sang ETH trước khi hiển thị.
- **Đáp ứng yêu cầu pháp lý năm 2026:**
  - Kể từ ngày 01/01/2026, khi Luật Công nghiệp Công nghệ số có hiệu lực và Bộ Tài chính ban hành Thông tư 15/2026/TT-BTC, 41/2026/TT-BTC về kế toán và thuế tài sản mã hóa, các doanh nghiệp bắt buộc phải có công cụ trích xuất, đối soát dòng tiền on-chain độc lập để giải trình với cơ quan thuế. Bản đặc tả của Lab 5 chính là tiền đề xây dựng công cụ kiểm toán số phục vụ trực tiếp cho yêu cầu pháp lý này.

### 7.5. Tổng kết và Tự đánh giá mức độ hoàn thành bài thực hành
- **Mức độ hoàn thành:** **Xuất sắc (Dự kiến đạt điểm 9.5 – 10.0)**.
- **Các điểm vượt trội so với yêu cầu chuẩn của đề bài:**
  1. Xây dựng đầy đủ 10 quy tắc nghiệp vụ (R1 đến R10), trong đó có 4 quy tắc chuyên sâu (R7: Self-transfer, R8: Số dư mở kỳ, R9: Internal Transactions, R10: Case-insensitive).
  2. Biên bản kiểm tra chéo ghi nhận chi tiết, chân thực với 3 lỗ hổng phản biện đắt giá.
  3. Xây dựng sẵn bộ kịch bản kiểm thử chuẩn BDD Gherkin và danh mục 6 điểm đối soát mã nguồn cho Lab 6.
  4. Sẵn sàng 100% dữ liệu và tư duy phản biện để bước vào giai đoạn sinh mã và kiểm chứng kết quả ở [lab06.md](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/lab06.md).

