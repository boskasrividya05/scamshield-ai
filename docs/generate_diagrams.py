"""
Generates architecture / workflow / ER diagram PNGs used in the project
report and PPT. Run: python generate_diagrams.py
Outputs into ./diagrams/
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams")
os.makedirs(OUT, exist_ok=True)

NAVY = "#0D1421"
CARD = "#131C2E"
BORDER = "#2A3A5C"
CYAN = "#29D8C8"
AMBER = "#FBBF24"
RED = "#F0505A"
GREEN = "#34D399"
TEXT = "#E7ECF5"
MUTED = "#9AA7BD"


def box(ax, xy, w, h, label, sub=None, color=CARD, edge=BORDER, text_color=TEXT, fontsize=11):
    x, y = xy
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                           linewidth=1.5, edgecolor=edge, facecolor=color)
    ax.add_patch(rect)
    if sub:
        ax.text(x + w / 2, y + h * 0.62, label, ha="center", va="center",
                 color=text_color, fontsize=fontsize, weight="bold", family="DejaVu Sans")
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center",
                 color=MUTED, fontsize=fontsize - 2.5, family="DejaVu Sans", wrap=True)
    else:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                 color=text_color, fontsize=fontsize, weight="bold", family="DejaVu Sans")
    return (x, y, w, h)


def arrow(ax, p1, p2, color=CYAN, style="-|>", lw=1.8):
    arr = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14,
                           color=color, linewidth=lw, shrinkA=2, shrinkB=2)
    ax.add_patch(arr)


def new_fig(w=14, h=8):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


# =====================================================================
# 1. SYSTEM ARCHITECTURE DIAGRAM
# =====================================================================
fig, ax = new_fig(14, 8.5)
ax.text(7, 8.1, "ScamShield AI — System Architecture", ha="center", color=TEXT,
        fontsize=18, weight="bold")

# Client layer
box(ax, (0.5, 6.2), 3, 1.3, "Client (Browser)", "HTML5 + CSS3 + JavaScript\n(Responsive UI)", color=CARD, edge=CYAN)
box(ax, (4.0, 6.2), 3, 1.3, "User Dashboard", "Chart.js visual analytics", color=CARD, edge=CYAN)
box(ax, (7.5, 6.2), 3, 1.3, "Admin Panel", "Reports & platform stats", color=CARD, edge=CYAN)
box(ax, (11.0, 6.2), 2.5, 1.3, "Fetch / AJAX", "Async JSON requests", color=CARD, edge=CYAN)

# Flask layer
box(ax, (0.5, 4.2), 13, 1.4, "Flask Web Server (app.py)",
    "Routes  ·  Session Auth  ·  Flash Messages  ·  Jinja2 Templates  ·  REST API endpoints",
    color=CARD, edge=BORDER, fontsize=13)

# Business logic layer
box(ax, (0.5, 2.3), 3.1, 1.4, "ml_utils.py", "TF-IDF + Logistic\nRegression Classifier", color=CARD, edge=GREEN)
box(ax, (3.9, 2.3), 3.1, 1.4, "Rule-Based Explainer", "Keyword matching +\nDigital Arrest detector", color=CARD, edge=AMBER)
box(ax, (7.3, 2.3), 3.1, 1.4, "URL / UPI Checkers", "Phishing pattern &\nUPI format validation", color=CARD, edge=RED)
box(ax, (10.7, 2.3), 2.8, 1.4, "db.py", "SQLite data access\nlayer", color=CARD, edge=CYAN)

# Data layer
box(ax, (2.5, 0.3), 4, 1.3, "SQLite Database", "users · scan_history ·\nscam_reports", color=CARD, edge=BORDER)
box(ax, (7.5, 0.3), 4, 1.3, "Trained Model Files", "fraud_model.pkl\nvectorizer.pkl", color=CARD, edge=BORDER)

# Arrows
arrow(ax, (2.0, 6.2), (2.0, 5.6))
arrow(ax, (5.5, 6.2), (5.5, 5.6))
arrow(ax, (9.0, 6.2), (9.0, 5.6))
arrow(ax, (12.2, 6.2), (12.2, 5.6))
arrow(ax, (2.0, 4.2), (2.0, 3.7))
arrow(ax, (5.5, 4.2), (5.5, 3.7))
arrow(ax, (9.0, 4.2), (9.0, 3.7))
arrow(ax, (12.0, 4.2), (12.0, 3.7))
arrow(ax, (4.5, 2.3), (4.5, 1.6))
arrow(ax, (9.5, 2.3), (9.5, 1.6))

plt.tight_layout()
plt.savefig(os.path.join(OUT, "architecture_diagram.png"), dpi=160, facecolor=NAVY)
plt.close()

# =====================================================================
# 2. WORKFLOW / SEQUENCE DIAGRAM (how a scan request is processed)
# =====================================================================
fig, ax = new_fig(14, 6.5)
ax.text(7, 6.1, "AI Fraud Detection — Workflow", ha="center", color=TEXT, fontsize=18, weight="bold")

steps = [
    ("1", "User Input", "SMS / Email / URL /\nUPI ID pasted by user", CYAN),
    ("2", "Preprocessing", "Text cleaned & converted\nto TF-IDF vector", GREEN),
    ("3", "ML Prediction", "Logistic Regression scores\nSafe / Suspicious / Fraud", AMBER),
    ("4", "Rule-Based Layer", "Keyword & Digital Arrest\npattern matching runs", RED),
    ("5", "Final Verdict", "Combined result + reasons\n+ prevention tips", CYAN),
    ("6", "Save & Display", "Logged to scan_history,\nshown on Dashboard", GREEN),
]

x = 0.4
w = 2.05
gap = 0.15
for i, (num, title, sub, color) in enumerate(steps):
    bx = x + i * (w + gap)
    box(ax, (bx, 3.2), w, 2.0, title, sub, color=CARD, edge=color, fontsize=10.5)
    ax.text(bx + w / 2, 5.45, num, ha="center", color=color, fontsize=15, weight="bold")
    if i < len(steps) - 1:
        arrow(ax, (bx + w, 4.2), (bx + w + gap, 4.2), color=MUTED)

# Digital arrest override note
box(ax, (0.4, 0.5), 13, 1.6,
    "Safety-Critical Override",
    "If ≥2 Digital Arrest keywords are matched (e.g. 'CBI officer', 'stay on video call',\n"
    "'do not disconnect'), the system force-classifies the input as FRAUD regardless of ML score,\n"
    "since false negatives on this scam type carry severe real-world risk.",
    color=CARD, edge=RED, fontsize=11)
arrow(ax, (7, 3.2), (7, 2.1), color=RED)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "workflow_diagram.png"), dpi=160, facecolor=NAVY)
plt.close()

# =====================================================================
# 3. ER DIAGRAM
# =====================================================================
fig, ax = new_fig(13, 7.5)
ax.text(6.5, 7.1, "Entity Relationship Diagram", ha="center", color=TEXT, fontsize=18, weight="bold")


def entity(ax, xy, w, title, fields, edge=CYAN):
    x, y = xy
    row_h = 0.42
    h = row_h * (len(fields) + 1)
    box(ax, (x, y), w, h, "", color=CARD, edge=edge)
    ax.text(x + w / 2, y + h - row_h / 2, title, ha="center", va="center",
            color=edge, fontsize=12.5, weight="bold")
    ax.plot([x, x + w], [y + h - row_h, y + h - row_h], color=edge, linewidth=1)
    for i, field in enumerate(fields):
        fy = y + h - row_h - row_h * (i + 1) + row_h / 2
        ax.text(x + 0.2, fy, field, ha="left", va="center", color=TEXT, fontsize=9.5)
    return (x, y, w, h)


users = entity(ax, (0.4, 4.3), 3.6, "USERS", [
    "PK  id",
    "    name",
    "    email (unique)",
    "    password_hash",
    "    is_admin",
    "    created_at",
], edge=CYAN)

scans = entity(ax, (5.0, 3.7), 3.9, "SCAN_HISTORY", [
    "PK  id",
    "FK  user_id",
    "    input_type",
    "    input_text",
    "    prediction",
    "    confidence",
    "    is_digital_arrest",
    "    created_at",
], edge=GREEN)

reports = entity(ax, (9.4, 4.3), 3.3, "SCAM_REPORTS", [
    "PK  id",
    "FK  user_id",
    "    scam_type",
    "    description",
    "    contact_info",
    "    status",
    "    created_at",
], edge=AMBER)

# relationship lines
ax.plot([users[0] + users[2], scans[0]], [users[1] + users[3] * 0.5, scans[1] + scans[3] * 0.6],
        color=MUTED, linewidth=1.4)
ax.text(4.55, 4.6, "1 : N", color=MUTED, fontsize=9)

ax.plot([scans[0] + scans[2], reports[0]], [scans[1] + scans[3] * 0.5, reports[1] + reports[3] * 0.4],
        color=MUTED, linewidth=1.4)
ax.text(9.05, 4.05, "1 : N", color=MUTED, fontsize=9)

ax.text(6.5, 0.6,
        "One user can have many scan_history records and many scam_reports.\n"
        "scam_reports.user_id can be NULL for anonymous/legacy reports.",
        ha="center", color=MUTED, fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "er_diagram.png"), dpi=160, facecolor=NAVY)
plt.close()

print("Diagrams generated in:", OUT)
