# PROJECT PLAN — HCE Student Crowdfund (Gây quỹ Dự án Sinh viên có Hoàn tiền)

Dự án thuộc học phần: **Tiền điện tử & Hợp đồng thông minh (ECO2432)**  
Kho mã nguồn nhóm: [`https://github.com/kadiciara299-lab/hce-crowdfunding-K57-.git`](https://github.com/kadiciara299-lab/hce-crowdfunding-K57-) (`hce-crowdfunding-K57-`)

---

## 1. Thành viên và phân công vai trò (Role Assignment & Rotation)

Theo quy chế học phần, nhóm 2 thành viên đảm nhiệm đầy đủ 4 vai trò nòng cốt: **Đặc tả nghiệp vụ (BA)**, **Hợp đồng thông minh (Smart Contract)**, **Giao diện Web DApp (Frontend)**, và **Kiểm thử & Đảm bảo chất lượng (QA/Auditor)** bằng cơ chế kiêm nhiệm và xoay vai giữa hai giai đoạn Lab 8–11 và Lab 12–15 để cả hai thành viên đều làm chủ toàn diện vòng đời sản phẩm Web3.

| STT | Họ và tên | Mã sinh viên | Vai chính Lab 8–11 (Khởi tạo & Dựng nền) | Vai chính Lab 12–15 (Bảo mật, Web & Tối ưu) | Trách nhiệm cụ thể |
| :-: | :--- | :---: | :--- | :--- | :--- |
| 1 | **Hoàng Mạnh Tường** *(Nhóm trưởng)* | **23K4300042** | **Đặc tả nghiệp vụ (BA) & Thiết kế Kinh tế** *(kiêm QA/Test)* | **Hợp đồng thông minh & Rà soát Bảo mật** *(kiêm Frontend DApp)* | Viết `SPEC.md`, `ECONOMIC_RULES.md`, điều phối nhóm; Giai đoạn 2 tối ưu gas, vá lỗi Reentrancy trong `ProjectCore.sol` và chủ trì Gate Review. |
| 2 | **Nguyễn Nguyên Phương** | **23K4300034** | **Hợp đồng thông minh (Smart Contract Dev)** *(kiêm Web/Gas)* | **Đặc tả nghiệp vụ & Thuyết trình (BA/Pitch)** *(kiêm Red Team Security)* | Phát triển `ProjectCore.sol`, đo đạc gas thực tế; Giai đoạn 2 chủ trì `PRESENTATION_PLAN.md`, kiểm thử tấn công Reentrancy và báo cáo kiểm toán chéo Lab 14. |

---

## 2. Người dùng và bài toán nghiệp vụ

### 2.1. Người dùng chính (Target Users)
1. **Chủ dự án (Campaign Creator):** Các cá nhân sinh viên, nhóm nghiên cứu sinh viên, ban chủ nhiệm Câu lạc bộ/Đội/Nhóm trực thuộc HCE cần huy động nguồn vốn hạt giống để triển khai đề tài NCKH, cuộc thi khởi nghiệp hoặc sự kiện sinh viên.
2. **Người đóng góp / Ủng hộ (Backers):** Sinh viên toàn trường, cựu sinh viên thành đạt, giảng viên, các doanh nghiệp đối tác muốn tài trợ kinh phí nhưng cần sự minh bạch và bảo đảm an toàn dòng tiền.

### 2.2. Vấn đề thực tế cần giải quyết (Core Problem)
- **Rủi ro mất vốn và thiếu minh bạch trong gây quỹ truyền thống:** Trước đây, sinh viên kêu gọi ủng hộ qua số tài khoản ngân hàng cá nhân hoặc ví MoMo. Nếu chiến dịch chỉ quyên góp được 2 triệu trên tổng mục tiêu 10 triệu cần thiết để làm dự án, dự án buộc phải hủy nhưng tiền ủng hộ thường bị "thất thoát", người đóng góp không được hoàn tiền hoặc phát sinh tranh cãi phức tạp do không có cơ chế hoàn tiền tự động.
- **Rủi ro chiếm dụng vốn (Rug Pull):** Người ủng hộ thiếu niềm tin rằng tiền của họ có thực sự được giải ngân đúng mục đích và chỉ khi dự án đủ điều kiện tài chính tối thiểu hay không.

### 2.3. Giải pháp sản phẩm (Proposed Solution)
Nền tảng **HCE Student Crowdfund** xây dựng trên hợp đồng thông minh blockchain:
- Tiền quyên góp được khoá tự động trong Smart Contract bảo chứng (Assurance Escrow), không ai có thể tự tiện rút ra.
- Nếu chiến dịch **đạt hoặc vượt mục tiêu** trước hạn chót $\rightarrow$ Chủ dự án được quyền rút vốn để tiến hành dự án.
- Nếu chiến dịch **hết hạn mà không đạt mục tiêu** $\rightarrow$ Hợp đồng tự động mở khóa hoàn tiền, cho phép từng người ủng hộ tự rút lại 100% số tiền đã góp mà không phụ thuộc vào ý chí của chủ dự án.

### 2.4. Sản phẩm cuối nhìn thấy được (Tangible Deliverables)
1. **Smart Contract lõi (`ProjectCore.sol`):** Hợp đồng quản lý chiến dịch gây quỹ có điều kiện, hoàn tiền tự động, bảo vệ chống tái nhập (ReentrancyGuard), kiểm soát trần/sàn đóng góp.
2. **Bộ ca kiểm thử tự động (`test/`):** Tối thiểu 5 ca kiểm thử bao gồm ca hợp lệ, ca vi phạm điều kiện thời gian, ca vi phạm số tiền và ca thử tấn công gian lận.
3. **Giao diện Web3 DApp (`web/index.html`):** Giao diện chạy mượt mà trên cả trình duyệt máy tính và điện thoại di động, kết nối trực tiếp ví MetaMask, hiển thị tiến độ gọi vốn trực quan theo thời gian thực.
4. **Hồ sơ tài liệu chuẩn (`docs/`):** Đầy đủ `PROJECT_PLAN.md`, `SPEC.md`, `ECONOMIC_RULES.md`, `AI_JOURNAL.md`, `AUDIT_REPORT.md` và `PRESENTATION_PLAN.md`.

---

## 3. Các mốc triển khai bắt buộc (Milestone Roadmap)

Tuân thủ nghiêm ngặt tiến trình đào tạo 15 bài thực hành của học phần ECO2432:

```mermaid
gantt
    title TIẾN ĐỘ TRIỂN KHAI DỰ ÁN HCE STUDENT CROWDFUND
    dateFormat  YYYY-MM-DD
    section Giai đoạn 1: Nền tảng
    Lab 08: Thiết kế kế hoạch & Quy tắc kinh tế   :done,    des1, 2026-10-04, 2026-10-05
    Lab 09: Lập trình Smart Contract lõi          :active,  des2, 2026-10-06, 2026-10-08
    Lab 10: Audit mã nguồn AI & Sửa lỗi           :         des3, 2026-10-09, 2026-10-11
    Lab 11: Cài đặt quy tắc kinh tế & Test        :         des4, 2026-10-12, 2026-10-14
    section Giai đoạn 2: Thẩm định & Mở rộng
    Lab 12: GATE REVIEW 1 (Duyệt Codebase & Phạm vi) :crit,   des5, 2026-10-15, 2026-10-16
    Lab 13: Thực nghiệm tấn công Reentrancy & Vá lỗi:         des6, 2026-10-17, 2026-10-19
    Lab 14: Rà soát chéo hợp đồng giữa các nhóm    :         des7, 2026-10-20, 2026-10-22
    Lab 15: Hoàn thiện DApp, Deploy & Demo        :crit,    des8, 2026-10-23, 2026-10-25
```

| Mốc bài Lab | Mục tiêu kỹ thuật & Sản phẩm đầu ra | Tiêu chí nghiệm thu (Acceptance Criteria) | Người chịu trách nhiệm chính |
| :--- | :--- | :--- | :---: |
| **Lab 8** *(Hiện tại)* | Khởi tạo codebase nhóm, kế hoạch dự án, đặc tả v0.1 và mô hình kinh tế | Repo nhóm có đủ 5 tệp trong `docs/`, cấu trúc thư mục chuẩn Phần B.6, hoàn thành phản biện mô hình kinh tế. | Hoàng Mạnh Tường |
| **Lab 9** | Hợp đồng lõi `ProjectCore.sol` biên dịch thành công trên Remix | Biên dịch Solidity ^0.8.20 không lỗi; thực hiện trọn vẹn luồng nạp và rút trên Remix VM; đo đạc bảng gas. | Nguyễn Nguyên Phương |
| **Lab 10** | Audit mã nguồn do AI sinh ra, nhận diện và sửa lỗi tiềm ẩn | Tìm ra ít nhất 3/4 lỗi cài cắm; ghi nhật ký `AI_JOURNAL.md` đối chiếu người phát hiện vs AI. | Hoàng Mạnh Tường |
| **Lab 11** | Cài đặt các quy tắc kinh tế vào contract và kiểm thử tự động | Cài đặt sàn/trần đóng góp và trần vượt quỹ; 1 test pass hợp lệ, 1 test revert vi phạm. | Nguyễn Nguyên Phương |
| **Lab 12** | **GATE REVIEW 1: Duyệt Codebase và Phạm vi** | Vượt qua cổng duyệt trực tiếp với giảng viên; demo 3 phút chứng minh luồng chính và ca vi phạm. | Cả 2 thành viên |
| **Lab 13** | Thực nghiệm tấn công mất tiền (Reentrancy Attack) và vá lỗi triệt để | Viết contract tấn công rút cạn quỹ; áp dụng Checks-Effects-Interactions vá lỗi; giải thích cơ chế. | Nguyễn Nguyên Phương |
| **Lab 14** | Rà soát chéo bảo mật với nhóm bạn | Lập báo cáo `AUDIT_REPORT.md` cho nhóm bạn theo bảng 10 tiêu chí; tiếp nhận và sửa lỗi cho nhóm mình. | Hoàng Mạnh Tường |
| **Lab 15** | Đưa DApp lên mạng công khai, kết nối ví và kịch bản thuyết trình | Deploy giao diện lên GitHub Pages; tương tác thành công trên điện thoại di động qua testnet Sepolia. | Cả 2 thành viên |
