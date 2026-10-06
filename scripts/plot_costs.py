"""
scripts/plot_costs.py
Vẽ biểu đồ so sánh chi phí vận hành on-chain L1 Ethereum vs Layer 2 (Lab 7)
Bổ sung Phân tích độ nhạy & Kiểm thử áp lực thị trường (Sensitivity Analysis)
"""

import os
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("evidence/lab-07", exist_ok=True)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)
fig.patch.set_facecolor("#0f172a")

# Biểu đồ 1: Thẻ tích điểm CLB (1.000 tx/tháng)
categories = ["L1 Ethereum\n(20k gas)", "L1 Ethereum\n(ERC-20 50k)", "Layer 2\n(20k gas)", "Layer 2\n(ERC-20 50k)"]
costs_usd = [1200.0, 3000.0, 12.0, 30.0]
colors = ["#ef4444", "#dc2626", "#10b981", "#059669"]

bars1 = ax1.bar(categories, costs_usd, color=colors, width=0.55, edgecolor="#ffffff", linewidth=0.8)
ax1.set_facecolor("#1e293b")
ax1.set_title("CHI PHÍ CLB SINH VIÊN (1.000 TX/THÁNG)", fontsize=10, fontweight="bold", color="#f8fafc", pad=12)
ax1.set_ylabel("Chi phí (USD/tháng)", fontsize=9, color="#cbd5e1")
ax1.tick_params(colors="#94a3b8", labelsize=8.5)
ax1.grid(axis="y", linestyle="--", alpha=0.25, color="#64748b")
for spine in ax1.spines.values():
    spine.set_color("#334155")

for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + (50 if yval > 100 else 1), f"${yval:,.1f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#f1f5f9")

# Biểu đồ 2: So sánh kinh tế dự án Ký quỹ KTX (Doanh thu vs Chi phí Gas)
project_labels = ["Doanh thu phí (1%)\n200 đơn", "Chi phí Gas L1\n(Mainnet)", "Chi phí Gas L2\n(Rollup)"]
project_values = [40.0, 960.0, 9.60]
project_colors = ["#38bdf8", "#ef4444", "#10b981"]

bars2 = ax2.bar(project_labels, project_values, color=project_colors, width=0.5, edgecolor="#ffffff", linewidth=0.8)
ax2.set_facecolor("#1e293b")
ax2.set_title("BÀI TOÁN DỰ ÁN KÝ QUỸ KTX (200 ĐƠN/THÁNG)", fontsize=10, fontweight="bold", color="#f8fafc", pad=12)
ax2.set_ylabel("Giá trị (USD/tháng)", fontsize=9, color="#cbd5e1")
ax2.tick_params(colors="#94a3b8", labelsize=8.5)
ax2.grid(axis="y", linestyle="--", alpha=0.25, color="#64748b")
for spine in ax2.spines.values():
    spine.set_color("#334155")

for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + (20 if yval > 100 else 1), f"${yval:,.1f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#f1f5f9")

# Biểu đồ 3: Phân tích độ nhạy - Chi phí gas 1 đơn KTX (L1 vs L2) qua 4 kịch bản thị trường
scenarios = ["1. Bear\n($2k/15g)", "2. Base\n($3k/20g)", "3. Bull\n($4k/40g)", "4. Spike\n($5k/80g)"]
l1_costs = [2.40, 4.80, 12.80, 32.00]
l2_costs = [0.024, 0.048, 0.128, 0.320]

x = np.arange(len(scenarios))
width = 0.35

ax3.set_facecolor("#1e293b")
bars3_l1 = ax3.bar(x - width/2, l1_costs, width, label="Ethereum L1 ($)", color="#ef4444", edgecolor="#ffffff", linewidth=0.8)
bars3_l2 = ax3.bar(x + width/2, l2_costs, width, label="Layer 2 ($)", color="#10b981", edgecolor="#ffffff", linewidth=0.8)

ax3.set_title("PHÂN TÍCH ĐỘ NHẠY CHI PHÍ / ĐƠN KTX (L1 VS L2)", fontsize=10, fontweight="bold", color="#f8fafc", pad=12)
ax3.set_ylabel("Phí gas / đơn hàng (USD)", fontsize=9, color="#cbd5e1")
ax3.set_xticks(x)
ax3.set_xticklabels(scenarios, color="#94a3b8", fontsize=8.5)
ax3.tick_params(colors="#94a3b8", labelsize=8.5)
ax3.grid(axis="y", linestyle="--", alpha=0.25, color="#64748b")
ax3.legend(facecolor="#334155", edgecolor="#475569", labelcolor="#f1f5f9", fontsize=8.5)
for spine in ax3.spines.values():
    spine.set_color("#334155")

for bar in bars3_l1:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 0.6, f"${yval:.1f}", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#f87171")

for bar in bars3_l2:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 0.6, f"${yval:.3f}", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#34d399")

plt.tight_layout()
plt.savefig("evidence/lab-07/cost_comparison.png", facecolor=fig.get_facecolor(), edgecolor="none")
plt.savefig("cost_comparison.png", facecolor=fig.get_facecolor(), edgecolor="none")
plt.close()
print("Saved evidence/lab-07/cost_comparison.png and cost_comparison.png with 3 subplots!")

