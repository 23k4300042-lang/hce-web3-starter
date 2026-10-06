# SPEC — HCE Student Crowdfund v0.1 (Nền tảng Gây quỹ Sinh viên có Hoàn tiền)

## 1. Mục đích
Hệ thống hợp đồng thông minh hỗ trợ các câu lạc bộ, nhóm sinh viên Trường Đại học Kinh tế - Đại học Huế (HCE) khởi tạo các chiến dịch huy động vốn cộng đồng cho các đề tài nghiên cứu khoa học, dự án khởi nghiệp và hoạt động tình nguyện; bảo đảm an toàn tuyệt đối cho người ủng hộ (sinh viên, cựu sinh viên, giảng viên, doanh nghiệp) thông qua cơ chế tự động khóa tiền bảo chứng và cam kết hoàn trả 100% vốn nếu dự án không đạt mục tiêu tài chính trước hạn chót.

---

## 2. Đầu vào (Inputs & Parameters)

| Tham số / Dữ liệu | Kiểu dữ liệu | Phạm vi giá trị | Đơn vị | Bên cung cấp | Diễn giải nghiệp vụ |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `creator` | `address` | Địa chỉ Ethereum hợp lệ, khác `address(0)` | Hex (42 ký tự) | Người tạo dự án | Địa chỉ ví đại diện cho nhóm sinh viên chủ trì dự án, là ví duy nhất được rút tiền khi chiến dịch thành công. |
| `fundingGoal` | `uint256` | $0.05 \text{ ETH} \le \text{Goal} \le 10 \text{ ETH}$ | wei | Người tạo dự án | Số vốn tối thiểu cần thiết để dự án có thể triển khai thực tế. Không cho phép đặt mục tiêu bằng 0. |
| `durationSeconds` | `uint256` | $3 \text{ ngày} \le \text{Duration} \le 30 \text{ ngày}$ | giây | Người tạo dự án | Khoảng thời gian chiến dịch mở nhận đóng góp. Giới hạn tối đa 30 ngày để tránh giam vốn người ủng hộ quá lâu. |
| `minContribution` | `uint256` | Mặc định: $0.001 \text{ ETH}$ ($10^{15} \text{ wei}$) | wei | Quy định hệ thống | Mức đóng góp tối thiểu cho mỗi lượt gửi tiền nhằm chống bão bụi giao dịch (dust attack) làm phình to lưu trữ on-chain. |
| `maxContributionPerWallet` | `uint256` | Mặc định: $25\%$ `fundingGoal` | wei | Quy định hệ thống | Hạn mức đóng góp tối đa trên một ví nhằm chống nguy cơ thao túng hoặc thống trị chiến dịch bởi một cá nhân. |
| `contributor` | `address` | Địa chỉ ví người gọi hàm | Hex (42 ký tự) | `msg.sender` | Ví thực hiện giao dịch đóng góp vốn hoặc yêu cầu rút tiền hoàn trả. |
| `msg.value` | `uint256` | `minContribution` $\le$ `msg.value` $\le$ Hạn mức ví còn lại | wei | Người ủng hộ | Số lượng tiền mã hóa ETH thực gửi kèm theo giao dịch đóng góp vốn. |

---

## 3. Quy tắc nghiệp vụ kiểm thử được (Testable Business Rules)

Mỗi quy tắc dưới đây là một khẳng định kỹ thuật có thể viết ca kiểm thử (Unit Test) xác thực độc lập:

- **R1 (Thời hạn đóng góp hợp lệ):** Người ủng hộ chỉ có thể gửi tiền vào chiến dịch khi thời điểm hiện tại nhỏ hơn thời điểm kết thúc (`block.timestamp < deadline`) VÀ chiến dịch đang ở trạng thái tiếp nhận (`state == State.Active`).
- **R2 (Hạn mức đóng góp):** Mỗi lượt đóng góp `msg.value` phải lớn hơn hoặc bằng `minContribution` VÀ tổng số tiền đã đóng góp của ví đó lũy kế không được vượt quá `maxContributionPerWallet`. Nếu vi phạm, hợp đồng phải từ chối ngay lập tức với lỗi tương ứng.
- **R3 (Khóa vốn bảo chứng):** Toàn bộ số ETH đóng góp được khóa an toàn trực tiếp trong số dư của hợp đồng thông minh. Tuyệt đối không ai (kể cả chủ dự án hay ban quản trị hệ thống) được phép rút tiền trước khi chiến dịch kết thúc hạn chót.
- **R4 (Rút vốn khi thành công - Successful Goal):** Khi thời gian đã hết (`block.timestamp >= deadline`), nếu tổng số vốn huy động được đạt hoặc vượt mục tiêu (`totalRaised >= fundingGoal`), chiến dịch chuyển sang trạng thái Thành công (`State.Successful`). **Duy nhất người tạo dự án (`msg.sender == creator`)** mới có quyền gọi hàm rút toàn bộ tiền về ví để triển khai dự án.
- **R5 (Hoàn tiền khi thất bại - Refund upon Failure):** Khi thời gian đã hết (`block.timestamp >= deadline`), nếu tổng số vốn huy động nhỏ hơn mục tiêu (`totalRaised < fundingGoal`), chiến dịch chuyển sang trạng thái Thất bại (`State.Failed`). **Bất kỳ người ủng hộ nào đã từng đóng góp (`contributions[msg.sender] > 0`)** đều có quyền yêu cầu hoàn trả lại đúng 100% số tiền họ đã góp.
- **R6 (Bảo vệ chống rút kép & tái nhập - CEI & Non-reentrancy):** Khi xử lý hoàn tiền, hệ thống phải ghi nhận xóa số dư đóng góp của người đó về 0 (`contributions[msg.sender] = 0`) TRƯỚC KHI chuyển ETH ra ngoài, bảo đảm không một ai có thể rút tiền lần thứ hai hoặc thực hiện tấn công tái nhập.
- **R7 (Minh bạch sự kiện On-chain):** Mọi hành vi thay đổi trạng thái bao gồm: Khởi tạo (`CampaignCreated`), Đóng góp (`Pledged`), Chủ dự án rút tiền (`FundsClaimed`), và Người ủng hộ hoàn tiền (`RefundClaimed`) đều bắt buộc phải phát ra `event` kèm đầy đủ tham số đánh chỉ mục (`indexed`) để tiện tra cứu trên Etherscan và cập nhật giao diện DApp.
- **R8 (Từ chối nhận tiền trực tiếp không chủ đích):** Mọi giao dịch chuyển tiền trực tiếp tới địa chỉ hợp đồng mà không gọi thông qua hàm đóng góp nghiệp vụ (`pledge()`) sẽ bị hàm `receive()` hoặc `fallback()` tự động từ chối (`revert`) để tránh người dùng bị mất tiền mà không được ghi nhận quyền lợi.

---

## 4. Đầu ra (Outputs & On-chain Events)

1. **Sự kiện ghi nhận trên Blockchain (Events):**
   - `event CampaignCreated(address indexed creator, uint256 goal, uint256 deadline, uint256 minContribution, uint256 maxContributionPerWallet);`
   - `event Pledged(address indexed contributor, uint256 amount, uint256 totalRaised);`
   - `event FundsClaimed(address indexed creator, uint256 amount);`
   - `event RefundClaimed(address indexed contributor, uint256 amount);`
2. **Dữ liệu trạng thái công khai (Public View Variables):**
   - Trạng thái hiện tại của chiến dịch (`state`: `Active`, `Successful`, `Failed`, `Claimed`).
   - Tổng số vốn đã huy động được (`totalRaised`).
   - Mục tiêu huy động (`fundingGoal`) và thời điểm kết thúc (`deadline`).
   - Số tiền đóng góp của từng địa chỉ ví (`contributions[address]`).
3. **Hiển thị trực quan trên giao diện DApp (`web/index.html`):**
   - Thanh tiến độ huy động vốn trực quan: `(totalRaised / fundingGoal) * 100%`.
   - Đồng hồ đếm ngược thời gian còn lại (Countdown timer).
   - Nút hành động tương ứng ngữ cảnh: *"Đóng góp vốn"* (khi đang diễn ra), *"Rút tiền dự án"* (cho Creator khi thành công), *"Yêu cầu hoàn tiền"* (cho Backer khi thất bại).

---

## 5. Trường hợp ngoại lệ (Edge Cases & Exception Handling)

Tuân thủ quy ước `AGENTS.md`, toàn bộ các trường hợp ngoại lệ đều được xử lý bằng `custom error` kèm tham số mô tả lỗi, thay thế hoàn toàn cho chuỗi thông báo dài trong `require`.

| Tình huống ngoại lệ | Điều kiện kích hoạt | Hành vi hệ thống | Mã lỗi tùy biến (`Custom Error`) |
| :--- | :--- | :--- | :--- |
| **E1: Góp tiền khi đã hết hạn** | `block.timestamp >= deadline` | Hủy giao dịch, hoàn trả toàn bộ gas thừa | `error CampaignEnded(uint256 deadline, uint256 currentTime);` |
| **E2: Đóng góp dưới mức tối thiểu** | `msg.value < minContribution` | Hủy giao dịch, không nhận tiền | `error ContributionTooLow(uint256 sent, uint256 minRequired);` |
| **E3: Đóng góp vượt trần một ví** | `contributions[msg.sender] + msg.value > maxContributionPerWallet` | Hủy giao dịch, chặn cá mập gom vốn | `error ExceedsMaxContribution(uint256 attempted, uint256 limit);` |
| **E4: Người lạ cố rút quỹ thành công** | `msg.sender != creator` khi gọi `claimFunds()` | Hủy giao dịch ngay tại bước Checks | `error OnlyCreatorAllowed();` |
| **E5: Rút tiền khi chưa hết hạn hoặc chưa đạt mục tiêu** | `block.timestamp < deadline` HOẶC `totalRaised < fundingGoal` | Hủy giao dịch, bảo vệ tiền của backers | `error GoalNotMet(uint256 raised, uint256 goal);` |
| **E6: Yêu cầu hoàn tiền khi chiến dịch thành công** | `totalRaised >= fundingGoal` khi gọi `claimRefund()` | Hủy giao dịch, không cho hoàn tiền khi dự án đã đạt mục tiêu | `error CampaignSucceeded();` |
| **E7: Yêu cầu hoàn tiền khi chưa hết hạn** | `block.timestamp < deadline` khi gọi `claimRefund()` | Hủy giao dịch, tiền vẫn đang trong kỳ huy động | `error CampaignStillActive(uint256 timeLeft);` |
| **E8: Đòi hoàn tiền khi không có số dư góp** | `contributions[msg.sender] == 0` | Hủy giao dịch, chống rút trộm | `error NoContributionToRefund();` |
| **E9: Lỗi đường truyền chuyển tiền ETH thất bại** | Lệnh `call{value: ...}("")` trả về `false` | Hoàn tác toàn bộ trạng thái giao dịch | `error TransferFailed();` |

---

## 6. Ngoài phạm vi (Out of Scope)

Để bảo đảm tính khả thi thực tế theo chuẩn sinh viên năm 3 và tiêu chí "Dưới 150 dòng mã nguồn cho `ProjectCore.sol`", các tính năng sau nằm **NGOÀI PHẠM VI** của phiên bản v0.1:
1. **Không phát hành Token phái sinh hoặc NFT cổ phần:** Không sử dụng chuẩn ERC-20 hay ERC-721 làm chứng chỉ đầu tư nhằm tránh biến dự án thành phát hành chứng khoán trái phép.
2. **Không tự động quy đổi tỷ giá VNĐ / Ngoại tệ on-chain:** Hợp đồng chỉ hạch toán thuần nhất bằng đơn vị tiền điện tử gốc của mạng lưới (ETH / Sepolia ETH), không tích hợp mạng tiên tri Chainlink Price Feeds phức tạp.
3. **Không theo dõi hóa đơn mua sắm off-chain sau khi giải ngân:** Hợp đồng bảo đảm cam kết 100% đến thời điểm bàn giao vốn cho chủ dự án. Việc giám sát chi tiêu đời thực của dự án thuộc phạm vi nghiệm thu của Đoàn trường/Hội sinh viên HCE theo quy chế thông thường.
