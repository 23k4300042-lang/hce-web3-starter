# HCE Student Crowdfund — Nền tảng Gây quỹ Dự án Sinh viên có Hoàn tiền

> **Một câu định vị sản phẩm:**  
> *"Nhóm xây dựng Nền tảng gây quỹ dự án sinh viên có hoàn tiền tự động (HCE Student Crowdfund) cho cộng đồng sinh viên và các câu lạc bộ Trường Đại học Kinh tế - Đại học Huế (HCE) nhằm huy động vốn minh bạch cho các đề tài nghiên cứu khoa học, dự án khởi nghiệp và cam kết tự động hoàn trả 100% tiền cho người ủng hộ nếu dự án không đạt mục tiêu tài chính trước hạn chót."*

---

## 👥 1. Thông tin Nhóm Sinh viên thực hiện (K57 Kinh Tế Số - HCE)

Dự án thuộc học phần: **Tiền điện tử & Hợp đồng thông minh (ECO2432)**  
Mã chủ đề đồ án: **Chủ đề 5 — Gây quỹ có hoàn tiền (Refundable Crowdfunding)**  
Kho mã nguồn chính thức: [`https://github.com/kadiciara299-lab/hce-crowdfunding-K57-.git`](https://github.com/kadiciara299-lab/hce-crowdfunding-K57-)

| STT | Họ và tên | Mã sinh viên | Vai chính Lab 8–11 | Vai chính Lab 12–15 | GitHub Username |
| :-: | :--- | :---: | :--- | :--- | :--- |
| 1 | **Hoàng Mạnh Tường** *(Lead)* | **23K4300042** | Đặc tả nghiệp vụ (BA) & Thiết kế Kinh tế *(kiêm QA)* | Hợp đồng thông minh & Audit *(kiêm Web3 Lead)* | `@manhtuong-k57` |
| 2 | **Nguyễn Nguyên Phương** | **23K4300034** | Hợp đồng thông minh *(kiêm Giao diện Web/Gas)* | Đặc tả & Thuyết trình *(kiêm Red Team Security)* | `@nguyenphuong-k57` |

---

## 📂 2. Cấu trúc Kho mã nguồn Chuẩn (Theo Phần B.6 Sổ tay)

```text
hce-crowdfunding-K57-/
├── README.md                      # Giới thiệu sản phẩm, thành viên và hướng dẫn chạy
├── AGENTS.md                      # Quy ước dự án bắt buộc cho công cụ AI
├── docs/
│   ├── PROJECT_PLAN.md            # Kế hoạch dự án, phân vai xoay vòng và 7 mốc bắt buộc
│   ├── SPEC.md                    # Bản đặc tả nghiệp vụ v0.1 có hiệu lực
│   ├── ECONOMIC_RULES.md          # Quy tắc dòng tiền, 4 rào cản chống lạm dụng & phản biện
│   ├── AI_JOURNAL.md              # Nhật ký làm việc với AI và các lỗi nghiêm trọng đã sửa
│   └── PRESENTATION_PLAN.md       # Kịch bản báo cáo và demo 5 phút phân công từng giây
├── contracts/
│   ├── training/                  # Hợp đồng mẫu học tập (TimeLockVault, VaultBuggy,...)
│   └── project/
│       └── ProjectCore.sol        # Hợp đồng thông minh cốt lõi của sản phẩm nhóm
├── test/                          # Ca kiểm thử tự động của sản phẩm nhóm
├── web/
│   └── index.html                 # Giao diện Web3 DApp kết nối MetaMask
└── evidence/
    └── lab-08/                    # Minh chứng commit, kiểm thử và biên bản từng lab
```

---

## 🚀 3. Hướng dẫn Chạy và Thử nghiệm

### 3.1. Biên dịch và Triển khai Hợp đồng trên Remix IDE
1. Truy cập [Remix Ethereum IDE](https://remix.ethereum.org).
2. Tải tệp `contracts/project/ProjectCore.sol` lên thư mục làm việc của Remix.
3. Trong tab **Solidity Compiler**, chọn phiên bản `0.8.20` trở lên và bấm **Compile ProjectCore.sol**.
4. Trong tab **Deploy & Run Transactions**:
   - Chọn môi trường: **Remix VM (Cancun / Shanghai)** để thử nghiệm tức thì miễn phí, hoặc **Injected Provider - MetaMask** để triển khai lên mạng thử nghiệm Sepolia.
   - Điền tham số Constructor:
     - `_goalInWei`: Ví dụ `1000000000000000000` (1 ETH).
     - `_durationSeconds`: Ví dụ `259200` (3 ngày tính bằng giây).
     - `_minContributionInWei`: Ví dụ `1000000000000000` (0.001 ETH).
   - Bấm **Deploy**.

### 3.2. Chạy Giao diện DApp Cục bộ
- Mở tệp `web/index.html` trực tiếp bằng trình duyệt Google Chrome hoặc Microsoft Edge đã cài đặt tiện ích MetaMask.
- Kết nối ví và chuyển mạng sang **Sepolia Testnet**.

---

## 📜 4. Cam kết Liêm chính và Quy ước Mã nguồn

- Toàn bộ mã nguồn tuân thủ nghiêm ngặt chỉ dẫn tại [`AGENTS.md`](./AGENTS.md):
  - Áp dụng nguyên tắc **Checks - Effects - Interactions** bảo vệ chống tấn công tái nhập.
  - Sử dụng lệnh chuyển tiền `call{value: ...}("")`, tuyệt đối không dùng `transfer`.
  - Khai báo lỗi tùy biến (`custom errors`) thay cho chuỗi ký tự lỗi dài trong `require`.
  - Đơn vị tính toán số học trên chuỗi luôn dùng `wei` và điểm cơ bản `basis points` ($1\% = 100 \text{ bps}$).
