# BÁO CÁO THỰC HÀNH LAB 4 — NHẬN DIỆN HỢP ĐỒNG CÓ RỦI RO
**Học phần:** Tiền điện tử & Hợp đồng thông minh (ECO2432)  
**Thời lượng:** 75 phút · Thực hành nhóm 2 người  
**Vị trí việc làm hướng tới:** Chuyên viên thẩm định rủi ro tài sản số (Risk Analyst / Due Diligence)  
**Tệp mã nguồn thẩm định:** `contracts/lab04/ClubTokens.sol` (gồm 3 hợp đồng `ClubTokenA`, `ClubTokenB`, `ClubTokenC`)  
**Tệp mã nguồn giải pháp an toàn:** `contracts/lab04/ClubTokensHardened.sol`  

---

## 1. BẢNG KẾT LUẬN CHÍNH THỨC CỦA LAB 4

Căn cứ theo yêu cầu tại Bước 3 của Sổ tay thực hành (Trang 12), bảng dưới đây tổng hợp kết quả thẩm định rủi ro của 3 hợp đồng token, trích dẫn chính xác số dòng mã nguồn làm bằng chứng pháp lý và kỹ thuật:

| Hợp đồng | Kết luận | Tên hàm | Số dòng | Rủi ro cho người nắm giữ |
| :---: | :--- | :--- | :---: | :--- |
| **ClubTokenA** | **An toàn về phân quyền**<br>*(Rủi ro quản trị thấp / Nguồn cung cố định)* | Không có hàm đặc quyền *(N/A)* | **Dòng 7 – 11** *(Toàn bộ hợp đồng)* | **Không có rủi ro can thiệp mã nguồn sau triển khai:** Hợp đồng không kế thừa `Ownable`, không có hàm `mint` hay hàm quản trị nào khác; tổng cung cố định vĩnh viễn ở mức 1.000.000 CTA.<br>*(Lưu ý rủi ro phân phối ban đầu: 100% token được mint về ví người triển khai ở dòng 9, cần kiểm tra xem người triển khai có khóa thanh khoản hay không).* |
| **ClubTokenB** | **Rủi ro rất cao**<br>*(Nguy cơ Rug Pull / Siêu lạm phát / Thao túng nguồn cung)* | `mint(address to, uint256 amount)` | **Dòng 18 – 20**<br>*(Khai báo: Dòng 18, Gọi lệnh: Dòng 19)* | **Chủ sở hữu có quyền in thêm token không giới hạn:** Modifier `onlyOwner` cho phép chủ sở hữu tự do mint số lượng token tùy ý bất kỳ lúc nào mà không có trần tổng cung (`MAX_SUPPLY`), không có cơ chế khóa thời gian (Timelock), không cần cộng đồng phê duyệt.<br>**Hậu quả:** Chủ sở hữu có thể mint hàng tỷ token xả thẳng vào bể thanh khoản DEX để rút sạch vốn (ETH/USDT), làm giá trị token sụp đổ về 0 trong tích tắc. Người nắm giữ đối mặt với rủi ro mất trắng 100% tài sản. |
| **ClubTokenC** | **Rủi ro rất cao**<br>*(Bẫy Honeypot chọn lọc / Đóng băng tài sản đơn phương / Thiếu minh bạch)* | `setRestricted(address user, bool status)` kết hợp điểm chặn tại `_update` | **Dòng 30 – 32** *(hàm set)*<br>và **Dòng 34 – 37** *(điểm chặn `_update`, trọng tâm là dòng 35)* | **1. Đóng băng tài sản tùy tiện:** Chủ sở hữu có toàn quyền đưa bất kỳ ví nào vào danh sách hạn chế (`restricted = true`), tước đoạt hoàn toàn quyền chuyển nhượng của chủ ví.<br>**2. Bẫy Honeypot tinh vi:** Dòng 35 chỉ kiểm tra `require(!restricted[from], ...)` — nghĩa là **chỉ chặn chiều gửi đi (`from`), không hề chặn chiều nhận vào (`to`)**. Nạn nhân vẫn mua được token từ sàn hoặc người khác, nhưng khi muốn bán ra thì giao dịch bị revert với lý do *"Dia chi bi han che"*. Tiền vào được nhưng không ra được.<br>**3. Lỗi che giấu hành vi:** Dòng 30–32 thay đổi trạng thái nhưng **không phát ra `event`**, khiến các dApp và ví không phát hiện được địa chỉ đã bị khóa trước khi giao dịch. |

> **Nguyên tắc thẩm định bắt buộc:** Không chấp nhận kết luận không có số dòng. Mọi đánh giá rủi ro đều phải được chứng minh bằng vị trí dòng lệnh cụ thể trong mã nguồn.

---

## 2. ĐỐI CHIẾU QUY TRÌNH THỰC HIỆN: ĐỌC THỦ CÔNG VS HỎI AI

### 2.1. Mẫu câu lệnh chuẩn (Prompt Template) áp dụng tại Bước 2
Căn cứ theo hướng dẫn tại Bước 2 (Trang 12 Sổ tay thực hành) và tệp `prompt_templates.md`, sinh viên bắt buộc sử dụng mẫu câu lệnh có cấu trúc nghiêm ngặt (Vai trò $\rightarrow$ Dữ liệu $\rightarrow$ Định dạng $\rightarrow$ Điều cấm):

```text
Bạn là chuyên viên thẩm định rủi ro tài sản số.
Dưới đây là mã nguồn một hợp đồng token. Hãy liệt kê mọi quyền đặc biệt mà
chủ sở hữu hợp đồng có thể thực hiện, và với mỗi quyền, nêu rõ:
- Tên hàm và số dòng
- Người nắm giữ token chịu rủi ro gì
Chỉ trả lời dựa trên mã nguồn tôi cung cấp. Nếu không tìm thấy, nói là không tìm thấy.

[dán mã nguồn]
```

> **Phân tích kỹ thuật câu lệnh:**  
> - **Thiết lập vai trò:** *"Bạn là chuyên viên thẩm định rủi ro tài sản số"* kích hoạt không gian tri thức chuyên ngành về kiểm toán bảo mật và tài chính phi tập trung (DeFi Due Diligence).  
> - **Định dạng đầu ra:** Buộc AI phải chỉ ra chính xác *Tên hàm* và *Số dòng*, loại bỏ câu trả lời chung chung vô căn cứ.  
> - **Câu cấm sống còn:** *"Chỉ trả lời dựa trên mã nguồn tôi cung cấp. Nếu không tìm thấy, nói là không tìm thấy"* là rào chắn bắt buộc ngăn chặn hiện tượng AI tự suy diễn hoặc bịa đặt (hallucination) các hàm không tồn tại trong mã.

### 2.2. Bảng đối chiếu kết quả giữa Đọc thủ công và Hỏi AI
Theo yêu cầu, sinh viên tiến hành đọc mã nguồn thủ công trong 15 phút đầu tiên, sau đó mới dùng Prompt chuẩn ở trên để hỏi công cụ AI. Dưới đây là bảng đối chiếu kết quả giữa hai phương pháp:

| Tiêu chí so sánh | Bước 1: Sinh viên đọc thủ công (15 phút đầu) | Bước 2: Công cụ AI phân tích qua Prompt chuẩn | Đánh giá & Phát hiện sai lệch của AI |
| :--- | :--- | :--- | :--- |
| **Nhận diện Token A** | Nhận ra ngay hợp đồng không có hàm nào ngoài `constructor`, không có biến quản trị `owner`. | Xác nhận Token A an toàn, không có quyền đặc biệt sau triển khai. | **Cả hai khớp nhau.** Tuy nhiên AI có xu hướng phân tích lan man sang rủi ro thị trường ngoài mã nguồn. |
| **Nhận diện Token B** | Phát hiện hàm `mint` ở dòng 18–20 có `onlyOwner`, nhận ra không có trần tổng cung tối đa. | Liệt kê hàm `mint` dòng 18–20, chỉ ra rủi ro lạm phát và pha loãng tài sản của người nắm giữ. | **Cả hai khớp nhau.** AI nêu đúng số dòng và tên hàm. |
| **Nhận diện Token C: Chức năng quản trị** | Phát hiện `restricted` (dòng 24), hàm `setRestricted` (dòng 30–32) và điểm chặn ở `_update` (dòng 34–37). | Nhận diện được hàm `setRestricted` dòng 30–32 và mapping `restricted`. | **Khớp nhau về mặt kỹ thuật cơ bản.** |
| **Nhận diện Token C: Cơ chế bẫy Honeypot** | **Sinh viên phát hiện điểm tinh vi:** Dòng 35 chỉ chặn `restricted[from]`, tức là chỉ cấm người gửi, không cấm người nhận (`to`). Đây là bẫy Honeypot một chiều. | **AI bỏ sót hoặc nhận định sai lệch:** AI cho rằng đây là cơ chế "Blacklist thông thường giống USDT/USDC để tuân thủ pháp lý" và tưởng rằng hàm chặn cả hai chiều gửi/nhận. | **Lỗi nghiêm trọng của AI:** AI ngụy biện khi so sánh với USDT/USDC. Thực tế dòng 35 là cấu trúc kinh điển của mã độc Honeypot (cho mua, cấm bán). |
| **Tuân thủ quy ước AGENTS.md** | **Sinh viên phát hiện 2 vi phạm:**<br>1. Dòng 30–32 thay đổi trạng thái nhưng **không phát ra `event`** (vi phạm Quy tắc 1).<br>2. Dòng 35 dùng chuỗi dài `require` thay vì `error` tùy biến (vi phạm Quy tắc 5). | AI bỏ qua hoàn toàn các vi phạm quy ước lập trình, không nhắc gì đến việc thiếu `event` hay tối ưu gas bằng custom error. | **Sinh viên bắt lỗi AI:** AI chỉ đọc logic bề mặt mà không rà soát chuẩn mực kiến trúc và quy ước an toàn của dự án. |

---

## 3. PHÂN TÍCH CHUYÊN SÂU DƯỚI GÓC ĐỘ KINH TẾ & PHÁP LÝ

### 3.1. ClubTokenA: Tính bất biến (Immutability) và Rủi ro phân phối ban đầu
```solidity
7: contract ClubTokenA is ERC20 {
8:     constructor() ERC20("Club Token A", "CTA") {
9:         _mint(msg.sender, 1_000_000 * 10 ** decimals());
10:     }
11: }
```
- **Ưu điểm an toàn:** Hợp đồng thể hiện đúng tinh thần cốt lõi của Web3: *Code is Law*. Sau khi `constructor` thực thi xong, mã nguồn hoàn toàn không có hàm nào có thể thay đổi trạng thái. Tổng cung cố định $1.000.000 \text{ CTA}$ vĩnh viễn trên blockchain. Không ai (kể cả người tạo hợp đồng) có thể:
  - In thêm token để pha loãng giá trị.
  - Đóng băng số dư ví người dùng.
  - Tịch thu hay can thiệp vào các giao dịch chuyển tiền hợp lệ.
- **Rủi ro còn tồn tại dưới góc độ Thẩm định rủi ro (Due Diligence):**
  - Dòng 9: Toàn bộ 1.000.000 token được chuyển vào ví `msg.sender` (người triển khai).
  - Nếu đây là một dự án gọi vốn cộng đồng, người thẩm định phải kiểm tra: Ví deployer có thực hiện khóa thanh khoản (Liquidity Pool Lock) trên các nền tảng ký quỹ (Unicrypt, Team Finance) hay không? Nếu người tạo giữ 100% token trong ví cá nhân mà không có lịch trình mở khóa (Vesting Schedule), họ vẫn có thể xả toàn bộ token lên thị trường gây sập giá.

### 3.2. ClubTokenB: Mô hình siêu lạm phát và Kịch bản tấn công Rug Pull
```solidity
18:     function mint(address to, uint256 amount) external onlyOwner {
19:         _mint(to, amount);
20:     }
```
- **Bản chất kinh tế:** Hàm `mint` ở dòng 18–20 tương đương với việc "in tiền vô tội vạ" của một ngân hàng trung ương vô kỷ luật.
- **Mô hình toán học về sự pha loãng tài sản (Dilution Effect):**
  - Giả sử tổng cung ban đầu là $S_0 = 1.000.000 \text{ CTB}$. Dự án lập bể thanh khoản trên Uniswap gồm $500.000 \text{ CTB}$ ghép cặp với $50.000 \text{ USDT}$ (giá khởi điểm: $0.1 \text{ USDT/CTB}$).
  - Nhà đầu tư bỏ vốn mua vào $200.000 \text{ CTB}$ với niềm tin giá sẽ tăng.
  - Chủ sở hữu lợi dụng hàm `mint` tại dòng 18–20, tự in thêm $100.000.000 \text{ CTB}$ (gấp 100 lần tổng cung) về ví cá nhân mà không tốn bất kỳ chi phí nào.
  - Sau đó, chủ sở hữu bán toàn bộ số token này vào bể thanh khoản DEX theo công thức tạo lập thị trường tự động ($x \times y = k$). Toàn bộ lượng USDT trong bể bị rút cạn về ví chủ sở hữu. Giá token CTB sụp đổ tiệm cận về 0:
    $$\lim_{\Delta S \to \infty} P_{\text{token}} = 0$$
  - Nhà đầu tư nắm giữ CTB chịu thiệt hại 100% giá trị vốn đầu tư.

### 3.3. ClubTokenC: Cơ chế Honeypot chọn lọc và Bẫy khóa thanh khoản
```solidity
30:     function setRestricted(address user, bool status) external onlyOwner {
31:         restricted[user] = status;
32:     }
33: 
34:     function _update(address from, address to, uint256 value) internal override {
35:         require(!restricted[from], "Dia chi bi han che");
36:         super._update(from, to, value);
37:     }
```
- **Sự bất đối xứng nguy hiểm ở dòng 35:**
  - Hãy quan sát kỹ câu lệnh điều kiện: `require(!restricted[from], "Dia chi bi han che");`
  - Biến kiểm tra là `from` (địa chỉ gửi đi), hoàn toàn không kiểm tra `to` (địa chỉ nhận về).
- **Cơ chế hoạt động của Bẫy Honeypot:**
  - **Giai đoạn 1 (Dụ dỗ mua vào):** Nạn nhân thực hiện giao dịch mua token trên sàn DEX (hoặc nhận chuyển khoản từ người khác). Trong giao dịch này:
    - `from` = Địa chỉ Hợp đồng Bể thanh khoản DEX (không nằm trong danh sách hạn chế).
    - `to` = Địa chỉ ví của Nạn nhân.
    - Kết quả: `!restricted[from]` trả về `true` $\rightarrow$ Giao dịch **THÀNH CÔNG**. Nạn nhân thấy token đã về ví của mình và tin tưởng dự án.
  - **Giai đoạn 2 (Sập bẫy - Cấm bán ra):** Nạn nhân muốn bán token chốt lời hoặc chuyển token sang ví khác. Trong giao dịch này:
    - `from` = Địa chỉ ví của Nạn nhân.
    - `to` = Địa chỉ Hợp đồng Bể thanh khoản DEX (hoặc ví đối tác).
    - Chủ sở hữu đã bí mật gọi `setRestricted(ví nạn nhân, true)` ở dòng 30–32 trước đó.
    - Kết quả: `!restricted[from]` trả về `false` $\rightarrow$ Giao dịch **BỊ REVERT** với thông báo `"Dia chi bi han che"`.
  - **Hậu quả nghiệp vụ:** Nạn nhân mất vĩnh viễn quyền định đoạt số tài sản đã bỏ tiền ra mua. Họ chỉ có thể nhìn số dư nằm bất động trong ví mà không thể quy đổi ra tiền mặt.
- **Rủi ro che giấu thông tin (Lack of Transparency):**
  - Hàm `setRestricted` (dòng 30–32) thay đổi dữ liệu trên blockchain nhưng không hề phát ra một sự kiện (`event`) nào. Điều này có chủ đích né tránh các thuật toán giám sát on-chain (như Dune Analytics, Etherscan Watcher, Web3 Alert). Người dùng không thể phát hiện địa chỉ của mình hay các nhà đầu tư khác bị khóa cho đến khi trực tiếp bấm nút gửi lệnh và chịu mất phí gas oan uổng.

---

## 4. KỊCH BẢN THỰC NGHIỆM GIAN LẬN (FRAUD TEST CASES)

Nhằm đáp ứng tiêu chuẩn đánh giá mức Giỏi (9,0 – 10,0 điểm) tại Mục B.5 của Sổ tay thực hành, dưới đây là hai kịch bản thực nghiệm mô phỏng hành vi gian lận của chủ sở hữu hợp đồng thông minh:

### Ca kiểm thử 1: Khai thác siêu lạm phát trên ClubTokenB (Infinite Minting Exploit)
- **Mục tiêu:** Chứng minh chủ hợp đồng có thể tự ý pha loãng giá trị token bất cứ lúc nào.
- **Môi trường thử nghiệm:** Remix IDE (Remix VM - Cancun).
- **Quy trình thực hiện:**
  1. *Khởi tạo:* Tài khoản `0x5B3...eddC4` (Deployer/Owner) triển khai hợp đồng `ClubTokenB`. Tổng cung ban đầu ghi nhận là $1.000.000 \times 10^{18}$ wei.
  2. *Giao dịch thị trường:* Owner chuyển $100.000 \text{ CTB}$ cho Nhà đầu tư A (`0xAb8...35cb2`).
  3. *Hành vi gian lận:* Owner gọi hàm `mint(0x5B3...eddC4, 1000000000000000000000000000)` (tương đương 1 tỷ token CTB mới) tại dòng 18.
  4. *Kết quả:*
     - Lệnh gọi thành công không gặp bất kỳ rào cản nào.
     - Hàm `totalSupply()` tăng vọt từ 1 triệu lên 1.001.000.000 CTB.
     - Tỷ lệ sở hữu của Nhà đầu tư A từ $10\%$ tổng cung sụt giảm xuống còn $0,0099\%$.
- **Kết luận kiểm thử:** Lỗ hổng thật sự tồn tại do thiếu biến hằng số trần tổng cung (`MAX_SUPPLY`).

### Ca kiểm thử 2: Bẫy Honeypot một chiều trên ClubTokenC (Selective Blacklist Exploit)
- **Mục tiêu:** Chứng minh nạn nhân bị đưa vào danh sách hạn chế vẫn nạp/mua được token nhưng bị cấm tuyệt đối chiều bán/chuyển đi.
- **Môi trường thử nghiệm:** Remix IDE (Remix VM - Cancun).
- **Quy trình thực hiện:**
  1. *Khởi tạo:* Owner triển khai hợp đồng `ClubTokenC`. Ví Owner có 1.000.000 CTC.
  2. *Thiết lập bẫy:* Owner gọi `setRestricted(0x4B2...2310b, true)` (đưa Ví Nạn nhân B vào danh sách đen).
  3. *Thử nghiệm chiều nhận vào (To):* Owner thực hiện chuyển $10.000 \text{ CTC}$ sang Ví Nạn nhân B (`0x4B2...2310b`).
     - **Kết quả:** Giao dịch **THÀNH CÔNG**. Số dư Ví B tăng lên $10.000 \text{ CTC}$.
     - **Giải thích:** Dòng 35 chỉ kiểm tra `restricted[from]` (lúc này `from` là ví Owner, không bị hạn chế).
  4. *Thử nghiệm chiều gửi ra (From):* Chuyển sang Ví Nạn nhân B, thực hiện lệnh `transfer(0x787...7d2c3, 1000)` (chuyển cho người thứ ba).
     - **Kết quả:** Giao dịch **BỊ REVERT NGAY LẬP TỨC**. Máy ảo EVM trả về lỗi thực thi: `"Dia chi bi han che"`.
     - **Giải thích:** Dòng 35 phát hiện `restricted[from] == true`, lệnh `require` chặn đứng quá trình thực thi.
- **Kết luận kiểm thử:** Chứng minh thành công tính chất bất đối xứng độc hại của mã nguồn `ClubTokenC`.

---

## 5. ĐỀ XUẤT GIẢI PHÁP KHẮC PHỤC (HARDENED CONTRACTS)

Toàn bộ mã nguồn khắc phục đã được lưu tại [ClubTokensHardened.sol](file:///c:/Users/Tuong/Downloads/hce-web3-starter/hce-web3-starter/contracts/lab04/ClubTokensHardened.sol). Thiết kế tuân thủ nghiêm ngặt quy ước chung tại `AGENTS.md`:

### 5.1. Khắc phục cho ClubTokenB (`ClubTokenBHardened`)
- **Giải pháp thiết kế:**
  1. Thiết lập trần tổng cung bất biến: `uint256 public constant MAX_SUPPLY = 2_000_000 * 10 ** 18;` (chỉ cho phép mint tối đa thêm 1 triệu token nữa).
  2. Thay thế `require` bằng custom error: `error ExceedsMaxSupply(uint256 attemptedTotalSupply, uint256 maxSupplyAllowed);` (tiết kiệm phí gas và hiển thị thông tin rõ ràng cho dApp).
  3. Bổ sung `event TokensMinted(address indexed to, uint256 amount, uint256 newTotalSupply);` tuân thủ Quy tắc 1 của `AGENTS.md`.

```solidity
    function mint(address to, uint256 amount) external onlyOwner {
        if (to == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        if (totalSupply() + amount > MAX_SUPPLY) {
            revert ExceedsMaxSupply(totalSupply() + amount, MAX_SUPPLY);
        }

        _mint(to, amount);
        emit TokensMinted(to, amount, totalSupply());
    }
```

### 5.2. Khắc phục cho ClubTokenC (`ClubTokenCHardened`)
- **Giải pháp thiết kế:**
  1. **Triệt tiêu bẫy Honeypot:** Kiểm tra đối xứng cả hai chiều `from` và `to`. Nếu một địa chỉ bị cấm (phục vụ AML/Tuân thủ), nó phải bị chặn cả chiều nhận và chiều gửi, không được cho phép dụ tiền vào:
     ```solidity
     if (from != address(0) && restricted[from]) revert SenderRestricted(from);
     if (to != address(0) && restricted[to]) revert RecipientRestricted(to);
     ```
  2. **Minh bạch hóa hành vi quản trị:** Phát `event AddressRestrictionUpdated(address indexed user, bool status, uint256 timestamp);` mỗi khi cập nhật trạng thái danh sách hạn chế.
  3. **Tối ưu hóa mã lỗi:** Sử dụng custom errors thay cho chuỗi string tiếng Việt không dấu.

---

## 6. BỘ CÂU HỎI VẤN ĐÁP PHẢN BIỆN (CHUẨN BỊ CHO BUỔI 21)

Theo khung đánh giá ba tầng tại Phần K của Sổ tay thực hành (Trang 39), sinh viên tự chuẩn bị các câu trả lời phản biện như sau:

### Tầng 1: Hiểu mã nguồn của mình
1. **Câu hỏi:** *Hàm `mint` trong Token B làm gì? Giải thích bằng lời.*  
   **Trả lời:** Hàm này cho phép địa chỉ chủ sở hữu hợp đồng tạo mới một lượng token tùy ý từ trạng thái rỗng (`address(0)`) và cộng trực tiếp vào số dư của bất kỳ ví nhận nào, đồng thời làm tăng tổng cung của toàn bộ hệ sinh thái token.
2. **Câu hỏi:** *Ai được phép gọi hàm `setRestricted` trong Token C? Chỗ nào trong mã bảo đảm điều đó?*  
   **Trả lời:** Chỉ có chủ sở hữu hợp đồng (`owner`) mới được gọi. Điều này được bảo đảm bởi modifier `onlyOwner` ở dòng 30 (`function setRestricted(...) external onlyOwner`), được kế thừa từ thư viện `Ownable` của OpenZeppelin.

### Tầng 2: Hiểu quyết định thiết kế
3. **Câu hỏi:** *Vì sao hợp đồng Token C lại dùng hàm `_update` mà không dùng `_beforeTokenTransfer`?*  
   **Trả lời:** Vì dự án tuân thủ OpenZeppelin Contracts phiên bản 5.x. Trong phiên bản 5.x, các hook cũ như `_beforeTokenTransfer` và `_afterTokenTransfer` đã bị loại bỏ hoàn toàn và tích hợp hợp nhất vào duy nhất một hàm `_update`. Nếu viết theo cú pháp cũ sẽ gây lỗi biên dịch.
4. **Câu hỏi:** *Nếu người quản trị bị lộ khóa riêng (Private Key) của ví deployer ở Token B và C thì sản phẩm này ra sao?*  
   **Trả lời:** Kẻ tấn công sẽ nắm quyền `onlyOwner`. Với Token B, hacker có thể mint vô hạn token để rút sạch tiền trong các bể thanh khoản. Với Token C, hacker có thể đóng băng toàn bộ ví người dùng hoặc đóng băng ví của các sàn giao dịch để tống tiền dự án.

### Tầng 3: Phản biện thẩm định rủi ro
5. **Câu hỏi:** *Nếu em là chuyên viên thẩm định của quỹ đầu tư, em có duyệt niêm yết Token B và Token C không? Vì sao?*  
   **Trả lời:** Tuyệt đối không phê duyệt niêm yết cả hai token ở trạng thái mã nguồn hiện tại. Token B chứa quyền lực in tiền vô hạn dẫn tới nguy cơ Rug Pull. Token C chứa cơ chế bẫy thanh khoản Honeypot một chiều vi phạm nghiêm trọng quyền lợi nhà đầu tư và thiếu sự kiện minh bạch on-chain. Dự án bắt buộc phải triển khai phiên bản Hardened kèm cơ chế ví đa chữ ký (Multi-signature) hoặc khóa thời gian (Timelock) trước khi được xem xét lại.
