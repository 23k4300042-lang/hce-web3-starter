# NHẬT KÝ LÀM VIỆC VỚI AI — Lab 2: Ví và Giao dịch Đầu tiên

## Lần 1
**Prompt:**  
"Giải thích điều gì xảy ra khi tôi sửa một ký tự trong địa chỉ ví người nhận rồi bấm gửi trên MetaMask. Giao dịch này có bị trừ phí gas không?"

**AI trả về:**  
AI trả lời rằng giao dịch sẽ được gửi lên mạng lưới Ethereum, nhưng các node/thợ đào khi kiểm tra thấy địa chỉ không hợp lệ sẽ hủy giao dịch (revert) và người gửi vẫn bị mất một khoản phí gas tối thiểu 21,000 gas cho công sức xác thực của mạng lưới.

**Đánh giá:** ❌ Sai, bỏ

**Chỗ sai:**  
AI nhầm lẫn giữa lỗi thực thi trên chuỗi (On-chain execution failure) với cơ chế kiểm tra định dạng tại giao diện người dùng (Client-side validation). Địa chỉ Ethereum có cơ chế phân biệt chữ hoa/chữ thường theo chuẩn **EIP-55 Checksum**. Khi sửa 1 ký tự, MetaMask phát hiện ngay lập tức chuỗi địa chỉ không hợp lệ về mặt checksum toán học và hiển thị cảnh báo đỏ *"Recipient address is invalid"* hoặc vô hiệu hóa nút Next/Confirm. Giao dịch hoàn toàn **chưa được ký và chưa được broadcast lên mempool**, nên người dùng **không mất bất kỳ khoản phí gas nào**.

**Cách sửa:**  
Sinh viên đối chiếu trực tiếp trên tiện ích MetaMask và tài liệu kỹ thuật EIP-55, đính chính lại cơ chế bảo vệ 2 lớp của ví và giải thích rõ sự khác biệt giữa lỗi Client-side (chặn trước khi phát mạng) và lỗi On-chain (đã phát mạng và tiêu tốn gas).

**Ai phát hiện:** Sinh viên phát hiện (khi thực hành kiểm thử Tình huống A trên MetaMask).

---

## Lần 2
**Prompt:**  
"Nếu ví tôi có đúng 0.01 ETH và tôi nhập số tiền chuyển là 0.01 ETH thì mạng lưới có tự động cấn trừ phí gas vào 0.01 ETH đó để chuyển số còn lại cho người nhận không?"

**AI trả về:**  
AI cho rằng cơ chế của blockchain tương tự như ngân hàng truyền thống hoặc cổng thanh toán, mạng lưới sẽ tự trừ phí giao dịch vào khoản tiền chuyển nên người nhận sẽ nhận được `0.01 ETH - Gas Fee`.

**Đánh giá:** ⚠️ Phải sửa

**Chỗ sai:**  
Mô hình giao dịch Ethereum quy định `Total Cost = Value + (Gas Limit * Gas Price)`. Số tiền chuyển (Value) và phí gas là hai khoản độc lập. Phí gas bắt buộc phải được người gửi chi trả thêm từ đồng tiền gốc (ETH) của ví gửi, không tự động cấn trừ vào Value của lệnh chuyển ETH thông thường. Do đó, MetaMask sẽ báo lỗi `Insufficient funds for gas * price + value` và không cho phép thực hiện nếu không còn số dư ETH để trả phí.

**Cách sửa:**  
Sinh viên sửa lại giải thích nghiệp vụ kế toán tài sản số: Doanh nghiệp muốn chuyển đủ giá trị định mức cho đối tác thì phải duy trì số dư gốc lớn hơn giá trị chuyển để chi trả chi phí mạng riêng biệt.

**Ai phát hiện:** Sinh viên phát hiện.

---

# NHẬT KÝ LÀM VIỆC VỚI AI — Lab 3: Đọc Giao dịch và Hợp đồng trên Etherscan

## Lần 3
**Prompt:**  
"Tôi đang mở hợp đồng USDC tại địa chỉ 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 trên Etherscan. Hãy chỉ cho tôi cách đọc tổng cung `totalSupply()` trong tab Read Contract."

**AI trả về:**  
AI hướng dẫn: "Bạn hãy vào tab Contract -> chọn tab Read Contract, tìm hàm số 5 có tên là `totalSupply()` và bấm Query để đọc tổng cung của USDC."

**Đánh giá:** ❌ Sai, bỏ

**Chỗ sai:**  
AI không nhận diện được kiến trúc hợp đồng thực tế của USDC là một **Upgradeable Proxy (chuẩn EIP-1967)**. Tại tab "Read Contract" thông thường của địa chỉ proxy `0xA0b86...`, Etherscan chỉ hiển thị các hàm quản trị proxy (`admin`, `implementation`, `upgradeTo`), hoàn toàn **không có hàm `totalSupply()` hay bất kỳ hàm nghiệp vụ ERC-20 nào**.  
Nếu làm theo AI, người dùng sẽ không tìm thấy hàm cần đọc.

**Cách sửa:**  
Sinh viên phát hiện đây là mô hình Proxy, chủ động chọn tab con **Read as Proxy** (hoặc truy cập thẳng vào địa chỉ Implementation Contract được chỉ định trong proxy) để Etherscan nạp đúng ABI của logic token, từ đó mới gọi được hàm `totalSupply()`.

**Ai phát hiện:** Sinh viên phát hiện (đối chiếu trực tiếp trên Etherscan).

---

# NHẬT KÝ LÀM VIỆC VỚI AI — Lab 4: Nhận diện Hợp đồng có Rủi ro

## Lần 4
**Prompt:**  
"Bạn là chuyên viên thẩm định rủi ro tài sản số.
Dưới đây là mã nguồn một hợp đồng token:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ClubTokenA is ERC20 {
    constructor() ERC20("Club Token A", "CTA") {
        _mint(msg.sender, 1_000_000 * 10 ** decimals());
    }
}

contract ClubTokenB is ERC20, Ownable {
    constructor() ERC20("Club Token B", "CTB") Ownable(msg.sender) {
        _mint(msg.sender, 1_000_000 * 10 ** decimals());
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}

contract ClubTokenC is ERC20, Ownable {
    mapping(address => bool) public restricted;

    constructor() ERC20("Club Token C", "CTC") Ownable(msg.sender) {
        _mint(msg.sender, 1_000_000 * 10 ** decimals());
    }

    function setRestricted(address user, bool status) external onlyOwner {
        restricted[user] = status;
    }

    function _update(address from, address to, uint256 value) internal override {
        require(!restricted[from], "Dia chi bi han che");
        super._update(from, to, value);
    }
}
```
Hãy liệt kê mọi quyền đặc biệt mà chủ sở hữu hợp đồng có thể thực hiện, và với mỗi quyền, nêu rõ:
- Tên hàm và số dòng
- Người nắm giữ token chịu rủi ro gì
Chỉ trả lời dựa trên mã nguồn tôi cung cấp. Nếu không tìm thấy, nói là không tìm thấy."

**AI trả về:**  
AI trả về danh sách phân tích:
- Token A: Không có quyền đặc biệt sau triển khai.
- Token B: Quyền `mint` ở dòng 18–20 cho phép chủ sở hữu in thêm token tùy ý, gây rủi ro lạm phát cho nhà đầu tư.
- Token C: Quyền `setRestricted` ở dòng 30–32 cho phép chủ sở hữu đưa ví người dùng vào danh sách đen (Blacklist). AI giải thích: *"Đây là cơ chế Blacklist thông thường nhằm tuân thủ pháp lý tương tự như USDT và USDC để ngăn chặn tội phạm rửa tiền. Khi một ví bị đưa vào danh sách hạn chế, toàn bộ các giao dịch gửi và nhận token của ví đó sẽ bị khóa hoàn toàn."*

**Đánh giá:** ⚠️ Phải sửa

**Chỗ sai:**  
1. **Hiểu sai logic kỹ thuật tại dòng 35:**
   `require(!restricted[from], "Dia chi bi han che");`
   Điều kiện kiểm tra chỉ là `!restricted[from]`, nghĩa là **chỉ chặn chiều gửi đi (`from`), hoàn toàn không chặn chiều nhận vào (`to`)**. Kết luận của AI rằng *"khóa toàn bộ giao dịch gửi và nhận"* là sai lệch kỹ thuật nghiêm trọng.
2. **Ngụy biện an toàn và bỏ qua bẫy Honeypot:**
   Việc AI so sánh cơ chế này với tính năng tuân thủ pháp lý của USDT/USDC là một đánh giá sai lầm nguy hại dưới góc độ thẩm định rủi ro. Sự bất đối xứng ở dòng 35 chính là bản chất của **Mã độc Bẫy Honeypot** (cho phép người dùng mua/nhận token vào ví bình thường, nhưng khi người dùng muốn bán ra hoặc chuyển đi thì giao dịch bị revert).
3. **Bỏ sót lỗi bảo mật và minh bạch:**
   Hàm `setRestricted` ở dòng 30–32 thay đổi trạng thái trong storage nhưng hoàn toàn không phát ra `event`, khiến cộng đồng và các dApp không thể nhận diện được hành vi đóng băng trên sổ cái.

**Cách sửa:**  
Sinh viên đính chính lại cơ chế Honeypot chọn lọc 1 chiều (chặn `from`, mở `to`), ghi nhận số dòng chính xác làm bằng chứng thẩm định và cảnh báo đây là rủi ro gian lận ở mức cao nhất chứ không phải tính năng tuân thủ thông thường.

**Ai phát hiện:** Sinh viên phát hiện (khi soi kỹ từng tham số của hàm `_update`).

---

## Lần 5
**Prompt:**  
"Hãy rà soát lại mã nguồn của `ClubTokenB` và `ClubTokenC` theo bộ quy chuẩn `AGENTS.md` của dự án ECO2432 (Solidity ^0.8.20, OpenZeppelin 5.x). Hãy chỉ rõ các điểm vi phạm quy tắc bắt buộc trong hợp đồng thông minh."

**AI trả về:**  
AI nhận định: Mã nguồn của cả hai hợp đồng đã hoàn toàn tuân thủ các quy tắc vì: (1) Sử dụng pragma Solidity `^0.8.20`; (2) Kế thừa chuẩn OpenZeppelin 5.x qua việc override hàm `_update` thay cho hook cũ `_beforeTokenTransfer`; (3) Các hàm nhạy cảm đều có modifier kiểm tra quyền hạn `onlyOwner`. Do đó hợp đồng không vi phạm quy tắc nào trong `AGENTS.md`.

**Đánh giá:** ❌ Sai, bỏ

**Chỗ sai:**  
AI chỉ kiểm tra cú pháp hình thức bên ngoài mà bỏ sót 2 quy tắc bắt buộc cốt lõi được quy định rõ trong `AGENTS.md`:
1. **Vi phạm Quy tắc 1 của `AGENTS.md`:** *"Mọi hàm làm thay đổi trạng thái phải phát ra một `event`."*  
   - Hàm `setRestricted` (dòng 30–32 của `ClubTokenC`) làm thay đổi biến trạng thái `restricted` nhưng hoàn toàn không phát ra sự kiện nào.
   - Hàm `mint` (dòng 18–20 của `ClubTokenB`) không phát sự kiện quản trị chuyên biệt nào ngoài sự kiện Transfer ngầm của thư viện.
2. **Vi phạm Quy tắc 5 của `AGENTS.md`:** *"Dùng `error` tùy biến thay cho chuỗi thông báo dài trong `require`."*  
   - Dòng 35 của `ClubTokenC` sử dụng chuỗi lỗi `require(!restricted[from], "Dia chi bi han che");` thay vì sử dụng cấu trúc `error` tùy biến để tiết kiệm chi phí gas và chuẩn hóa thông báo lỗi.

**Cách sửa:**  
Sinh viên trích dẫn lại 2 quy tắc trong `AGENTS.md`, chỉ ra số dòng vi phạm cụ thể trong mã nguồn, và tự thiết kế phiên bản hợp đồng an toàn `ClubTokensHardened.sol` khắc phục toàn bộ các vi phạm trên.

**Ai phát hiện:** Sinh viên phát hiện (đối chiếu trực tiếp với các điều khoản trong `AGENTS.md`).

---

# NHẬT KÝ LÀM VIỆC VỚI AI — Lab 6: Sinh mã bằng AI và Kiểm tra Kết quả

## Lần 6
**Prompt:**  
"Đọc tệp SPEC.md trong dự án và viết chương trình Python thực hiện đúng đặc tả đó. Tuân thủ các quy ước trong AGENTS.md. Trước khi viết mã, hãy tóm tắt lại cách bạn hiểu yêu cầu để tôi xác nhận."

**AI trả về:**  
AI tóm tắt lại bài toán nhưng khi sinh đoạn mã xử lý giao dịch thì viết như sau:
```python
for tx in transactions:
    if tx.get("isError") == "1":
        continue  # Giao dịch thất bại thì bỏ qua
    # ... xử lý giao dịch thành công
```

**Đánh giá:** ❌ Sai, bỏ

**Chỗ sai:**  
AI đã bỏ qua hoàn toàn các giao dịch thất bại bằng lệnh `continue`.  
Theo cơ chế máy ảo Ethereum và **Quy tắc R4 trong SPEC.md**: Khi một giao dịch gửi đi bị thất bại (`isError == "1"` và `from == target_address`), số tiền chuyển `value` đúng là không bị trừ, nhưng **toàn bộ chi phí gas mạng (`gasUsed * gasPrice`) vẫn bị trừ vĩnh viễn khỏi ví của người gửi**.  
Nếu bỏ qua giao dịch này, số dư kế toán sẽ bị lệch so với số dư thực tế trên chuỗi, làm sai lệch báo cáo dòng tiền ra (Outflow) và kiểm toán AML.

**Cách sửa:**  
Sinh viên yêu cầu AI sửa lại nhánh điều kiện: Khi `isError == "1"` và `from.lower() == target_address.lower()`, ghi nhận loại giao dịch `OUT_FAILED` với giá trị chuyển $0 \text{ ETH}$ và dòng tiền ra bằng đúng chi phí gas mạng đã tiêu hao.

**Ai phát hiện:** Sinh viên phát hiện (đối chiếu danh mục kiểm tra Mục 4 của Lab 6 và Quy tắc R4 trong `SPEC.md`).

---

## Lần 7
**Prompt:**  
"Hãy bổ sung cấu hình để chương trình kết nối và truy xuất dữ liệu từ mạng thử nghiệm Sepolia Testnet bằng Etherscan API."

**AI trả về:**  
AI sinh đoạn mã cấu hình như sau:
```python
API_KEY = "ABC123XYZ456"  # Hoặc điền key trực tiếp vào đây nếu không có biến môi trường
if network == "sepolia":
    base_url = "https://api-sepolia.etherscan.io/api"
else:
    base_url = "https://api.etherscan.io/api"
```

**Đánh giá:** ❌ Sai, bỏ

**Chỗ sai:**  
1. **Vi phạm nghiêm trọng Quy tắc 1 của `AGENTS.md` (Bảo mật khóa API):** AI gợi ý hardcode chuỗi API key dự phòng trực tiếp trong mã nguồn. Nếu đẩy lên GitHub, khóa này sẽ bị quét và thu hồi ngay lập tức.
2. **Dùng endpoint API v1 đã cũ (Mục 6 danh mục kiểm tra):** AI sử dụng endpoint cũ `api-sepolia.etherscan.io`. Theo tài liệu Etherscan hiện hành, nền tảng đã chuyển dịch sang giao diện **API v2 Multichain Hợp nhất** (`https://api.etherscan.io/v2/api`), trong đó phân biệt các mạng bằng tham số `chainid` (`chainid=11155111` cho Sepolia, `chainid=1` cho Ethereum Mainnet). Dữ liệu huấn luyện của AI đã cũ nên tự động dùng endpoint phiên bản trước.

**Cách sửa:**  
- Sinh viên loại bỏ hoàn toàn mọi dòng hardcode API key, buộc chương trình chỉ đọc qua `os.environ.get("ETHERSCAN_API_KEY")`.
- Cập nhật hàm gọi API sang chuẩn **Etherscan API v2 Multichain**, đồng thời bổ sung cờ dự phòng tương thích ngược.

**Ai phát hiện:** Sinh viên phát hiện (đối chiếu tài liệu Etherscan API v2 và quy ước bảo mật trong `AGENTS.md`).

---

# NHẬT KÝ LÀM VIỆC VỚI AI — Lab 7: Tính Chi phí Vận hành Thực tế

## Lần 8
**Prompt:**  
"Một câu lạc bộ sinh viên dự kiến phát hành thẻ tích điểm trên blockchain với 1.000 lượt cộng điểm/tháng. Đơn giá gas là 20 Gwei, giá ETH là 3.000 USD. Bạn hãy tư vấn lựa chọn mạng lưới blockchain triển khai phù hợp nhất cho dự án này."

**AI trả về:**  
AI tính toán chi phí gas ra khoảng 1.200 USD/tháng và đưa ra lời khuyên:  
*"Bạn nên triển khai hợp đồng thẻ tích điểm trực tiếp trên Ethereum Mainnet (Layer 1) để đảm bảo mức độ bảo mật cao nhất, tính phi tập trung tuyệt đối và dữ liệu không thể bị giả mạo. Chi phí 1.200 USD/tháng (~30 triệu VNĐ) là mức chi phí vận hành hạ tầng công nghệ thông tin hoàn toàn hợp lý và xứng đáng cho một câu lạc bộ đại học."*

**Đánh giá:** ❌ Sai, bỏ

**Chỗ sai:**  
AI hoàn toàn **thiếu cảm quan kinh tế vi mô (Economic Common Sense) và không hiểu bối cảnh tài chính thực tế**:  
1. **Quy mô ngân sách câu lạc bộ sinh viên:** Quỹ hoạt động của một câu lạc bộ sinh viên thông thường chỉ dao động từ vài trăm nghìn đến vài triệu VNĐ/tháng. Việc phải chi trả từ 30.000.000 đến 76.000.000 VNĐ/tháng chỉ để duy trì việc ghi điểm thưởng sẽ khiến câu lạc bộ phá sản ngay tháng đầu tiên!  
2. **Kinh tế học hành vi người dùng:** Nếu chuyển phần phí này cho sinh viên tự trả ($1,20 \text{ USD} \approx 30.500 \text{ VNĐ}$ cho mỗi lần quét mã cộng điểm), thì **chi phí giao dịch (Transaction Cost) cao gấp nhiều lần giá trị điểm thưởng hoặc ly nước**, chắc chắn 100% sinh viên sẽ tẩy chay sản phẩm.  
3. **Mù mờ về giải pháp mở rộng Layer 2:** AI không đề xuất mạng Lớp 2 (Layer 2 Rollups: Base, Arbitrum, Optimism) với chi phí rẻ hơn 100 lần (chỉ còn $12 \text{ USD/tháng} \approx 300.000 \text{ VNĐ}$), hoặc kiến trúc Tài trợ gas (Paymaster / Account Abstraction ERC-4337) để mang lại trải nghiệm miễn phí gas cho sinh viên.

**Cách sửa:**  
Sinh viên bác bỏ đề xuất của AI, phân tích chi tiết bài toán kinh tế vi mô và kết luận: DApp thẻ tích điểm **bắt buộc phải triển khai trên Layer 2**, sử dụng Paymaster tài trợ phí từ quỹ CLB ($12 \text{ USD/tháng}$) để đạt tính khả thi thương mại.

**Ai phát hiện:** Sinh viên phát hiện (phân tích tính khả thi kinh tế tại Bước 2 Lab 7).


