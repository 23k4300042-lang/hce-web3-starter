// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ClubTokenAHardened
 * @dev Hợp đồng A đã an toàn về mặt phân quyền do không có quyền quản trị sau triển khai.
 * Phiên bản Hardened bổ sung Event minh bạch hóa lượng phát hành ban đầu.
 */
contract ClubTokenAHardened is ERC20 {
    event InitialTokensMinted(address indexed recipient, uint256 amount);

    constructor() ERC20("Club Token A Hardened", "CTAh") {
        uint256 initialSupply = 1_000_000 * 10 ** decimals();
        _mint(msg.sender, initialSupply);
        emit InitialTokensMinted(msg.sender, initialSupply);
    }
}

/**
 * @title ClubTokenBHardened
 * @dev Khắc phục rủi ro lạm phát vô hạn và Rug Pull ở Token B:
 * 1. Thiết lập trần tổng cung cứng (MAX_SUPPLY).
 * 2. Dùng custom error `ExceedsMaxSupply` thay cho chuỗi require.
 * 3. Phát `event TokensMinted` khi mint thành công tuân thủ AGENTS.md.
 */
contract ClubTokenBHardened is ERC20, Ownable {
    uint256 public constant MAX_SUPPLY = 2_000_000 * 10 ** 18; // Trần tổng cung 2 triệu token

    event TokensMinted(address indexed to, uint256 amount, uint256 newTotalSupply);

    error ExceedsMaxSupply(uint256 attemptedTotalSupply, uint256 maxSupplyAllowed);
    error ZeroAmount();
    error ZeroAddress();

    constructor() ERC20("Club Token B Hardened", "CTBh") Ownable(msg.sender) {
        uint256 initialSupply = 1_000_000 * 10 ** decimals();
        _mint(msg.sender, initialSupply);
        emit TokensMinted(msg.sender, initialSupply, initialSupply);
    }

    function mint(address to, uint256 amount) external onlyOwner {
        if (to == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        if (totalSupply() + amount > MAX_SUPPLY) {
            revert ExceedsMaxSupply(totalSupply() + amount, MAX_SUPPLY);
        }

        _mint(to, amount);
        emit TokensMinted(to, amount, totalSupply());
    }
}

/**
 * @title ClubTokenCHardened
 * @dev Khắc phục rủi ro bẫy Honeypot và đóng băng đơn phương ở Token C:
 * 1. Chặn 2 chiều đối xứng (cả `from` và `to`), loại bỏ bẫy "cho mua nhưng cấm bán".
 * 2. Phát `event AddressRestrictionUpdated` công khai để ví/dApp theo dõi on-chain.
 * 3. Dùng custom error `SenderRestricted` và `RecipientRestricted` theo chuẩn AGENTS.md.
 */
contract ClubTokenCHardened is ERC20, Ownable {
    mapping(address => bool) public restricted;

    event AddressRestrictionUpdated(address indexed user, bool status, uint256 timestamp);

    error SenderRestricted(address sender);
    error RecipientRestricted(address recipient);
    error ZeroAddress();

    constructor() ERC20("Club Token C Hardened", "CTCh") Ownable(msg.sender) {
        uint256 initialSupply = 1_000_000 * 10 ** decimals();
        _mint(msg.sender, initialSupply);
    }

    function setRestricted(address user, bool status) external onlyOwner {
        if (user == address(0)) revert ZeroAddress();
        restricted[user] = status;
        emit AddressRestrictionUpdated(user, status, block.timestamp);
    }

    function _update(address from, address to, uint256 value) internal override {
        // Kiểm tra đối xứng cả chiều gửi và chiều nhận (chống bẫy Honeypot)
        if (from != address(0) && restricted[from]) {
            revert SenderRestricted(from);
        }
        if (to != address(0) && restricted[to]) {
            revert RecipientRestricted(to);
        }

        super._update(from, to, value);
    }
}
