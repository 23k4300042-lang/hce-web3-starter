// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title HCE Student Crowdfund Core Contract
/// @notice Nen tang gay quy du an sinh vien co co che hoan tien tu dong (All-or-Nothing)
/// @dev Tuan thu nghiem ngat AGENTS.md: Solidity ^0.8.20, Checks-Effects-Interactions, Custom Errors
contract ProjectCore {
    // 1. Dinh nghia trang thai chien dich
    enum State { Active, Successful, Failed, Claimed }

    // 2. Bien trang thai bat bien va luu tru
    address public immutable creator;
    uint256 public immutable fundingGoal;
    uint256 public immutable deadline;
    uint256 public immutable minContribution;
    uint256 public immutable maxContributionPerWallet;

    uint256 public totalRaised;
    State public state;
    mapping(address => uint256) public contributions;

    // 3. Su kien on-chain
    event CampaignCreated(address indexed creator, uint256 goal, uint256 deadline);
    event Pledged(address indexed contributor, uint256 amount, uint256 currentTotal);
    event FundsClaimed(address indexed creator, uint256 totalAmount);
    event RefundClaimed(address indexed contributor, uint256 refundAmount);
    event StateUpdated(State newState);

    // 4. Custom Errors theo quy uoc AGENTS.md
    error InvalidCreator();
    error InvalidGoal();
    error InvalidDuration();
    error CampaignEnded(uint256 deadline, uint256 currentTime);
    error ContributionTooLow(uint256 sent, uint256 minRequired);
    error ExceedsMaxContribution(uint256 attempted, uint256 limit);
    error OnlyCreatorAllowed();
    error GoalNotMet(uint256 raised, uint256 goal);
    error CampaignStillActive(uint256 timeLeft);
    error CampaignSucceeded();
    error NoContributionToRefund();
    error AlreadyClaimed();
    error TransferFailed();

    constructor(
        uint256 _goalInWei,
        uint256 _durationSeconds,
        uint256 _minContributionInWei
    ) {
        if (msg.sender == address(0)) revert InvalidCreator();
        if (_goalInWei == 0) revert InvalidGoal();
        // Gioi han thoi gian chien dich tu 3 ngay den 30 ngay
        if (_durationSeconds < 3 days || _durationSeconds > 30 days) revert InvalidDuration();

        creator = msg.sender;
        fundingGoal = _goalInWei;
        deadline = block.timestamp + _durationSeconds;
        minContribution = _minContributionInWei > 0 ? _minContributionInWei : 0.001 ether;
        maxContributionPerWallet = (_goalInWei * 25) / 100; // Tran 25% muc tieu
        state = State.Active;

        emit CampaignCreated(creator, fundingGoal, deadline);
    }

    /// @notice Nguoi ung ho dong gop ETH vao chien dich
    function pledge() external payable {
        // 1. Checks
        if (block.timestamp >= deadline) revert CampaignEnded(deadline, block.timestamp);
        if (state != State.Active) revert CampaignEnded(deadline, block.timestamp);
        if (msg.value < minContribution) revert ContributionTooLow(msg.value, minContribution);

        uint256 newTotalContribution = contributions[msg.sender] + msg.value;
        if (newTotalContribution > maxContributionPerWallet) {
            revert ExceedsMaxContribution(newTotalContribution, maxContributionPerWallet);
        }

        // 2. Effects
        contributions[msg.sender] = newTotalContribution;
        totalRaised += msg.value;

        emit Pledged(msg.sender, msg.value, totalRaised);
    }

    /// @notice Chu du an rut toan bo quy khi chien dich thanh cong
    function claimFunds() external {
        // 1. Checks
        if (msg.sender != creator) revert OnlyCreatorAllowed();
        if (state == State.Claimed) revert AlreadyClaimed();
        if (block.timestamp < deadline && totalRaised < fundingGoal) {
            revert CampaignStillActive(deadline - block.timestamp);
        }
        if (totalRaised < fundingGoal) revert GoalNotMet(totalRaised, fundingGoal);

        // 2. Effects
        state = State.Claimed;
        uint256 amountToTransfer = address(this).balance;

        emit FundsClaimed(creator, amountToTransfer);
        emit StateUpdated(State.Claimed);

        // 3. Interactions: Chuyen tien bang call theo quy uoc AGENTS.md
        (bool success, ) = payable(creator).call{value: amountToTransfer}("");
        if (!success) revert TransferFailed();
    }

    /// @notice Nguoi ung ho rut lai 100% tien khi chien dich that bai
    function claimRefund() external {
        // 1. Checks
        if (block.timestamp < deadline) revert CampaignStillActive(deadline - block.timestamp);
        if (totalRaised >= fundingGoal) revert CampaignSucceeded();

        uint256 contributedAmount = contributions[msg.sender];
        if (contributedAmount == 0) revert NoContributionToRefund();

        // 2. Effects: Xoa so du TRUOC de chong Reentrancy Attack
        contributions[msg.sender] = 0;
        if (state != State.Failed) {
            state = State.Failed;
            emit StateUpdated(State.Failed);
        }

        emit RefundClaimed(msg.sender, contributedAmount);

        // 3. Interactions: Chuyen tien sau cung
        (bool success, ) = payable(msg.sender).call{value: contributedAmount}("");
        if (!success) revert TransferFailed();
    }

    /// @notice Tra ve thoi gian con lai cua chien dich tinh bang giay
    function timeLeft() external view returns (uint256) {
        if (block.timestamp >= deadline) return 0;
        return deadline - block.timestamp;
    }

    /// @dev Tu choi moi giao dich chuyen ETH truc tiep khong thong qua ham pledge()
    receive() external payable {
        revert ContributionTooLow(0, minContribution);
    }
}
