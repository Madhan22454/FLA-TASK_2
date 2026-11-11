"""Generate crisp, mathematically exact automata diagrams in diagrams/.

Produces:
    - diagrams/pin_dfa.png          (ATM PIN 6-state DFA + transition table)
    - diagrams/password_dfa.png     (Password 5 component DFAs + Product DFA model)
    - diagrams/email_automaton.png  (Email 9-state NFA & Minimal 8-state DFA)
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch


OUT_DIR = Path(__file__).resolve().parent / "diagrams"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NAVY = "#0F2C59"
BLUE = "#1D4ED8"
LIGHT_BLUE = "#EFF6FF"
ACCEPT_FILL = "#DCFCE7"
ACCEPT_EDGE = "#15803D"
TRAP_FILL = "#FEE2E2"
TRAP_EDGE = "#B91C1C"
SLATE = "#334155"
BORDER = "#CBD5E1"


def draw_state(
    ax: plt.Axes,
    x: float,
    y: float,
    label: str,
    radius: float = 0.42,
    initial: bool = False,
    accepting: bool = False,
    trap: bool = False,
    subtitle: str = "",
    subtitle_offset: Tuple[float, float] = (0.0, 0.0),
) -> None:
    """Draw a formal automaton state node with optional initial arrow & double circle."""
    if accepting:
        fc, ec = ACCEPT_FILL, ACCEPT_EDGE
    elif trap:
        fc, ec = TRAP_FILL, TRAP_EDGE
    else:
        fc, ec = LIGHT_BLUE, NAVY

    outer = Circle((x, y), radius, facecolor=fc, edgecolor=ec, linewidth=2.0, zorder=4)
    ax.add_patch(outer)

    if accepting:
        inner = Circle(
            (x, y), radius * 0.80, facecolor="none", edgecolor=ec, linewidth=1.6, zorder=5
        )
        ax.add_patch(inner)

    ax.text(
        x,
        y,
        label,
        ha="center",
        va="center",
        fontsize=10.0,
        fontweight="bold",
        color="#0F172A",
        zorder=6,
    )

    if subtitle:
        ax.text(
            x + subtitle_offset[0],
            y - radius - 0.16 + subtitle_offset[1],
            subtitle,
            ha="center",
            va="top",
            fontsize=7.8,
            color=SLATE,
            zorder=6,
        )

    if initial:
        arrow = FancyArrowPatch(
            (x - radius - 0.70, y),
            (x - radius - 0.03, y),
            arrowstyle="-|>,head_length=7,head_width=4",
            linewidth=2.0,
            color=NAVY,
            zorder=5,
        )
        ax.add_patch(arrow)
        ax.text(
            x - radius - 0.72,
            y + 0.14,
            "start",
            ha="left",
            va="bottom",
            fontsize=8.5,
            fontstyle="italic",
            color=NAVY,
        )


def draw_edge(
    ax: plt.Axes,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    label: str,
    r1: float = 0.42,
    r2: float = 0.42,
    rad: float = 0.0,
    label_pos: Tuple[float, float] | None = None,
    label_offset: Tuple[float, float] = (0.0, 0.18),
    color: str = SLATE,
    fontsize: float = 8.4,
) -> None:
    """Draw a directed transition edge between two state centers."""
    arrow = FancyArrowPatch(
        p1,
        p2,
        shrinkA=r1 * 72 * 0.45,
        shrinkB=r2 * 72 * 0.45,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>,head_length=6.5,head_width=3.6",
        linewidth=1.5,
        color=color,
        zorder=3,
    )
    ax.add_patch(arrow)

    if label_pos is not None:
        lx, ly = label_pos
    else:
        lx = (p1[0] + p2[0]) / 2.0 + label_offset[0]
        ly = (p1[1] + p2[1]) / 2.0 + label_offset[1]

    ax.text(
        lx,
        ly,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="bold",
        color=color,
        bbox=dict(boxstyle="round,pad=0.14", facecolor="white", edgecolor="none", alpha=0.90),
        zorder=7,
    )


def draw_self_loop(
    ax: plt.Axes,
    x: float,
    y: float,
    label: str,
    radius: float = 0.42,
    direction: str = "top",
    color: str = SLATE,
    fontsize: float = 8.2,
) -> None:
    """Draw a clean self-loop arc on a state."""
    if direction == "top":
        start = (x - 0.17, y + radius * 0.92)
        end = (x + 0.17, y + radius * 0.92)
        rad = -1.65
        lx, ly = x, y + radius + 0.48
    elif direction == "bottom":
        start = (x - 0.17, y - radius * 0.92)
        end = (x + 0.17, y - radius * 0.92)
        rad = 1.65
        lx, ly = x, y - radius - 0.48
    else:
        start = (x + radius * 0.92, y + 0.17)
        end = (x + radius * 0.92, y - 0.17)
        rad = -1.65
        lx, ly = x + radius + 0.62, y

    arrow = FancyArrowPatch(
        start,
        end,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>,head_length=6,head_width=3.5",
        linewidth=1.45,
        color=color,
        zorder=3,
    )
    ax.add_patch(arrow)
    ax.text(
        lx,
        ly,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="bold",
        color=color,
        bbox=dict(boxstyle="round,pad=0.14", facecolor="white", edgecolor="none", alpha=0.92),
        zorder=7,
    )


def generate_pin_diagram() -> Path:
    """Create diagrams/pin_dfa.png with full 6-state DFA and transition table."""
    fig = plt.figure(figsize=(11.5, 6.4), dpi=300, facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[2.35, 1.35], hspace=0.12)

    ax = fig.add_subplot(gs[0])
    ax.set_xlim(-1.4, 11.4)
    ax.set_ylim(-2.65, 1.85)
    ax.axis("off")

    ax.text(
        5.0,
        1.58,
        "Application 1: ATM PIN Verification DFA  "
        r"($\Sigma = \{0,1,\dots,9\},\; L_{\mathrm{PIN}} = \{w \in \Sigma^* : |w| = 4\}$)",
        ha="center",
        va="center",
        fontsize=12.5,
        fontweight="bold",
        color=NAVY,
    )

    coords = {
        "q0": (0.2, 0.38),
        "q1": (2.5, 0.38),
        "q2": (4.8, 0.38),
        "q3": (7.1, 0.38),
        "q4": (9.4, 0.38),
        "q_trap": (4.8, -1.65),
    }

    draw_state(ax, *coords["q0"], "q0", initial=True, subtitle="0 digits")
    draw_state(ax, *coords["q1"], "q1", subtitle="1 digit")
    draw_state(ax, *coords["q2"], "q2", subtitle="2 digits")
    draw_state(ax, *coords["q3"], "q3", subtitle="3 digits")
    draw_state(ax, *coords["q4"], "q4", accepting=True, subtitle="4 digits (Accept)")
    draw_state(
        ax,
        *coords["q_trap"],
        "q_trap",
        trap=True,
        subtitle="Dead sink (len > 4 or ∉ Σ)",
        subtitle_offset=(0.0, -0.50),
    )

    for src, dst in [("q0", "q1"), ("q1", "q2"), ("q2", "q3"), ("q3", "q4")]:
        draw_edge(
            ax,
            coords[src],
            coords[dst],
            "0–9",
            label_offset=(0.0, 0.22),
            color=BLUE,
        )

    draw_edge(
        ax,
        coords["q4"],
        coords["q_trap"],
        "0–9, ∉Σ",
        rad=-0.20,
        label_pos=(7.55, -0.92),
        color=TRAP_EDGE,
    )
    draw_edge(ax, coords["q0"], coords["q_trap"], "∉Σ", rad=0.20, label_pos=(2.05, -0.92), color=TRAP_EDGE)
    draw_edge(ax, coords["q1"], coords["q_trap"], "∉Σ", rad=0.08, label_pos=(3.42, -0.68), color=TRAP_EDGE)
    draw_edge(ax, coords["q2"], coords["q_trap"], "∉Σ", rad=0.0, label_pos=(5.04, -0.62), color=TRAP_EDGE)
    draw_edge(ax, coords["q3"], coords["q_trap"], "∉Σ", rad=-0.08, label_pos=(6.18, -0.68), color=TRAP_EDGE)

    draw_self_loop(ax, *coords["q_trap"], "0–9, ∉Σ", direction="right", color=TRAP_EDGE)

    ax_tbl = fig.add_subplot(gs[1])
    ax_tbl.axis("off")
    col_labels = ["State", "Description", "Input d ∈ {0..9}", "Invalid Char (∉ Σ)", "Accepting?"]
    table_data = [
        ["-> q0", "Initial state (0 digits read)", "q1", "q_trap", "No"],
        ["q1", "1 valid numeric digit read", "q2", "q_trap", "No"],
        ["q2", "2 valid numeric digits read", "q3", "q_trap", "No"],
        ["q3", "3 valid numeric digits read", "q4", "q_trap", "No"],
        ["* q4", "Exactly 4 numeric digits read", "q_trap", "q_trap", "Yes"],
        ["q_trap", "Dead/rejecting sink state", "q_trap", "q_trap", "No"],
    ]
    tbl = ax_tbl.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
        colWidths=[0.12, 0.34, 0.20, 0.20, 0.14],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.8)
    tbl.scale(1.0, 1.38)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(BORDER)
        if r == 0:
            cell.set_facecolor(NAVY)
            cell.set_text_props(color="white", fontweight="bold")
        elif r == 5:
            cell.set_facecolor("#F0FDF4")
        elif r == 6:
            cell.set_facecolor("#FEF2F2")
        else:
            cell.set_facecolor("#F8FAFC" if r % 2 == 0 else "white")

    out_path = OUT_DIR / "pin_dfa.png"
    fig.savefig(out_path, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return out_path


def generate_password_diagram() -> Path:
    """Create diagrams/password_dfa.png showing modular component DFAs & product DFA."""
    fig = plt.figure(figsize=(12.8, 7.9), dpi=300, facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[2.75, 1.25], hspace=0.14)

    ax = fig.add_subplot(gs[0])
    ax.set_xlim(-1.2, 14.2)
    ax.set_ylim(-3.85, 2.85)
    ax.axis("off")

    ax.text(
        6.5,
        2.56,
        "Application 2: Password Policy Product DFA  "
        r"($L_{\mathrm{PWD}} = L_{\mathrm{len}} \cap L_U \cap L_L \cap L_D \cap L_S$,  "
        r"$\Sigma = \{U, L, D, S, O\}$)",
        ha="center",
        va="center",
        fontsize=12.0,
        fontweight="bold",
        color=NAVY,
    )

    # Top box: Component M_len (0..16 + len_trap)
    box1 = FancyBboxPatch(
        (-0.9, 0.15), 14.8, 2.05, boxstyle="round,pad=0.12",
        facecolor="#F8FAFC", edgecolor=BORDER, linewidth=1.2, zorder=1
    )
    ax.add_patch(box1)
    ax.text(
        -0.65,
        2.00,
        "Component 1: Length & Allowed-Alphabet DFA  M_len  (18 states, F = {8, ..., 16})",
        ha="left",
        va="center",
        fontsize=9.5,
        fontweight="bold",
        color=NAVY,
    )

    len_nodes = [
        ("0", 0.1, True, False),
        ("1", 1.7, False, False),
        ("...", 3.3, False, False),
        ("7", 4.9, False, False),
        ("8", 6.5, False, True),
        ("...", 8.1, False, True),
        ("16", 9.7, False, True),
        ("len_trap", 12.2, False, False),
    ]
    for lbl, x, init, acc in len_nodes:
        if lbl == "...":
            ax.text(x, 1.05, "...", ha="center", va="center", fontsize=14, fontweight="bold", color=SLATE)
        else:
            r = 0.44 if lbl == "len_trap" else 0.35
            draw_state(ax, x, 1.05, lbl, radius=r, initial=init, accepting=acc, trap=(lbl == "len_trap"))

    for x1, x2, txt in [
        (0.1, 1.7, "U,L,D,S"),
        (1.7, 3.3, "U,L,D,S"),
        (3.3, 4.9, "U,L,D,S"),
        (4.9, 6.5, "U,L,D,S"),
        (6.5, 8.1, "U,L,D,S"),
        (8.1, 9.7, "U,L,D,S"),
    ]:
        draw_edge(ax, (x1, 1.05), (x2, 1.05), txt, r1=0.35, r2=0.35, label_offset=(0, 0.24), fontsize=7.6, color=BLUE)

    draw_edge(ax, (9.7, 1.05), (12.2, 1.05), "Σ", r1=0.35, r2=0.44, label_offset=(0, 0.22), fontsize=8.4, color=TRAP_EDGE)
    draw_edge(
        ax,
        (4.9, 1.05),
        (12.2, 1.05),
        "O (from any 0..16)",
        r1=0.35,
        r2=0.44,
        rad=0.25,
        label_pos=(8.55, 0.35),
        fontsize=7.8,
        color=TRAP_EDGE,
    )
    draw_self_loop(ax, 12.2, 1.05, "Σ", radius=0.44, direction="top", color=TRAP_EDGE, fontsize=8.2)

    # Bottom-left: 4 class-tracking 2-state DFAs
    box2 = FancyBboxPatch(
        (-0.9, -3.65), 6.4, 3.45, boxstyle="round,pad=0.12",
        facecolor="#F8FAFC", edgecolor=BORDER, linewidth=1.2, zorder=1
    )
    ax.add_patch(box2)
    ax.text(
        2.3,
        -0.42,
        "Components 2–5: Class DFAs  (M_X, X ∈ {U, L, D, S})",
        ha="center",
        va="center",
        fontsize=9.3,
        fontweight="bold",
        color=NAVY,
    )

    draw_state(ax, 0.55, -1.62, "X0", radius=0.36, initial=True, subtitle="X not seen")
    draw_state(ax, 3.85, -1.62, "X1", radius=0.36, accepting=True, subtitle="X seen (Accept)")
    draw_edge(ax, (0.55, -1.62), (3.85, -1.62), "X", r1=0.36, r2=0.36, label_offset=(0, 0.20), color=BLUE, fontsize=9.0)
    draw_self_loop(ax, 0.55, -1.62, "Σ \\ {X}", radius=0.36, direction="top", color=SLATE, fontsize=8.0)
    draw_self_loop(ax, 3.85, -1.62, "Σ", radius=0.36, direction="top", color=ACCEPT_EDGE, fontsize=8.0)
    ax.text(
        2.3,
        -2.92,
        "Instantiated for each required class:\n"
        "• M_U (U0 → U1 on U)    • M_L (L0 → L1 on L)\n"
        "• M_D (D0 → D1 on D)    • M_S (S0 → S1 on S)",
        ha="center",
        va="center",
        fontsize=8.2,
        color="#0F172A",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=BORDER),
    )

    # Bottom-right: Product DFA architecture box
    box3 = FancyBboxPatch(
        (5.9, -3.65), 8.0, 3.45, boxstyle="round,pad=0.12",
        facecolor="#EFF6FF", edgecolor=BLUE, linewidth=1.4, zorder=1
    )
    ax.add_patch(box3)
    ax.text(
        9.9,
        -0.42,
        "Product DFA:  M_PWD = M_len × M_U × M_L × M_D × M_S",
        ha="center",
        va="center",
        fontsize=9.5,
        fontweight="bold",
        color=NAVY,
    )
    ax.text(
        9.9,
        -2.05,
        "State Tuple:  q = (len, u, l, d, s)   with   0 ≤ len ≤ 16,  u,l,d,s ∈ {0,1}\n"
        "Initial State:  q0 = (0, U0, L0, D0, S0)\n"
        "Accepting States (9):  {(k, U1, L1, D1, S1) : 8 ≤ k ≤ 16}\n"
        "Trap State (q_trap):  entered immediately on class O or length > 16\n\n"
        "Reachable Product States: 225  (Complete: 225 × 5 = 1,125 transitions)\n"
        "Hopcroft/Moore Minimized DFA: 197 states  (28 dead states merged into q_trap)",
        ha="center",
        va="center",
        fontsize=8.5,
        color="#0F172A",
        linespacing=1.45,
        bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor=BORDER),
    )

    # Transition rule table
    ax_tbl = fig.add_subplot(gs[1])
    ax_tbl.axis("off")
    col_labels = ["State Pattern", "U (Upper)", "L (Lower)", "D (Digit)", "S (Special)", "O (Other)"]
    table_data = [
        ["-> (0, U0, L0, D0, S0)", "(1,U1,L0,D0,S0)", "(1,U0,L1,D0,S0)", "(1,U0,L0,D1,S0)", "(1,U0,L0,D0,S1)", "q_trap"],
        ["(k, u, l, d, s), k < 16", "(k+1, U1, l, d, s)", "(k+1, u, L1, d, s)", "(k+1, u, l, D1, s)", "(k+1, u, l, d, S1)", "q_trap"],
        ["* (k, U1, L1, D1, S1), 8≤k<16", "(k+1,U1,L1,D1,S1)", "(k+1,U1,L1,D1,S1)", "(k+1,U1,L1,D1,S1)", "(k+1,U1,L1,D1,S1)", "q_trap"],
        ["(16, u, l, d, s)  [incl. *]", "q_trap", "q_trap", "q_trap", "q_trap", "q_trap"],
        ["q_trap (Dead Sink)", "q_trap", "q_trap", "q_trap", "q_trap", "q_trap"],
    ]
    tbl = ax_tbl.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
        colWidths=[0.25, 0.16, 0.16, 0.16, 0.16, 0.11],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.0)
    tbl.scale(1.0, 1.38)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(BORDER)
        if r == 0:
            cell.set_facecolor(NAVY)
            cell.set_text_props(color="white", fontweight="bold")
        elif r == 3:
            cell.set_facecolor("#F0FDF4")
        elif r == 5:
            cell.set_facecolor("#FEF2F2")
        else:
            cell.set_facecolor("#F8FAFC" if r % 2 == 0 else "white")

    out_path = OUT_DIR / "password_dfa.png"
    fig.savefig(out_path, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return out_path


def generate_email_diagram() -> Path:
    """Create diagrams/email_automaton.png with 9-state NFA and Minimal 8-state DFA."""
    fig = plt.figure(figsize=(13.2, 10.2), dpi=300, facecolor="white")
    gs = fig.add_gridspec(3, 1, height_ratios=[1.65, 2.05, 1.35], hspace=0.18)

    # Panel 1: 9-state NFA
    ax1 = fig.add_subplot(gs[0])
    ax1.set_xlim(-1.4, 15.2)
    ax1.set_ylim(-1.35, 2.35)
    ax1.axis("off")
    ax1.text(
        6.9,
        2.12,
        "Application 3 (Part A): 9-State Email Format NFA  "
        r"($\Sigma = \{\mathrm{A}, \mathrm{D}, \mathrm{DOT}, \mathrm{HYP}, \mathrm{UND}, \mathrm{AT}, \mathrm{OTHER}\}$)",
        ha="center",
        va="center",
        fontsize=11.5,
        fontweight="bold",
        color=NAVY,
    )

    nfa_pos = {
        "n0": (0.0, 0.15),
        "n1": (2.2, 0.15),
        "n2": (2.2, 1.32),
        "n3": (4.6, 0.15),
        "n4": (7.0, 0.15),
        "n5": (7.0, 1.32),
        "n6": (9.5, -0.55),
        "n7": (11.8, -0.55),
        "n8": (14.1, -0.55),
    }
    for st, pos in nfa_pos.items():
        draw_state(
            ax1,
            *pos,
            st,
            radius=0.37,
            initial=(st == "n0"),
            accepting=(st == "n8"),
        )

    draw_edge(ax1, nfa_pos["n0"], nfa_pos["n1"], "A, D", r1=0.37, r2=0.37, label_pos=(1.1, 0.36), color=BLUE)
    draw_self_loop(ax1, *nfa_pos["n1"], "A, D", radius=0.37, direction="bottom", color=BLUE)
    draw_edge(ax1, nfa_pos["n1"], nfa_pos["n2"], "DOT,HYP,UND", r1=0.37, r2=0.37, rad=-0.30, label_pos=(1.22, 0.78), fontsize=7.5)
    draw_edge(ax1, nfa_pos["n2"], nfa_pos["n1"], "A, D", r1=0.37, r2=0.37, rad=-0.30, label_pos=(2.85, 0.78), fontsize=7.8, color=BLUE)
    draw_edge(ax1, nfa_pos["n1"], nfa_pos["n3"], "AT (@)", r1=0.37, r2=0.37, label_pos=(3.4, 0.36), color=NAVY)
    draw_edge(ax1, nfa_pos["n3"], nfa_pos["n4"], "A, D", r1=0.37, r2=0.37, rad=-0.18, label_pos=(5.8, 0.56), color=BLUE)
    draw_self_loop(ax1, *nfa_pos["n4"], "A, D", radius=0.37, direction="bottom", color=BLUE)
    draw_edge(ax1, nfa_pos["n4"], nfa_pos["n5"], "HYP (-)", r1=0.37, r2=0.37, rad=-0.30, label_pos=(6.25, 0.78), fontsize=7.5)
    draw_edge(ax1, nfa_pos["n5"], nfa_pos["n4"], "A, D", r1=0.37, r2=0.37, rad=-0.30, label_pos=(7.62, 0.78), fontsize=7.8, color=BLUE)
    draw_edge(ax1, nfa_pos["n4"], nfa_pos["n3"], "DOT (next label)", r1=0.37, r2=0.37, rad=-0.34, label_pos=(5.65, -0.58), fontsize=7.6, color="#7C3AED")
    draw_edge(ax1, nfa_pos["n4"], nfa_pos["n6"], "DOT (guess TLD)", r1=0.37, r2=0.37, rad=0.10, label_pos=(8.45, 0.05), fontsize=7.6, color="#7C3AED")
    draw_edge(ax1, nfa_pos["n6"], nfa_pos["n7"], "A", r1=0.37, r2=0.37, label_pos=(10.65, -0.35), color=ACCEPT_EDGE)
    draw_edge(ax1, nfa_pos["n7"], nfa_pos["n8"], "A", r1=0.37, r2=0.37, label_pos=(12.95, -0.35), color=ACCEPT_EDGE)
    draw_self_loop(ax1, *nfa_pos["n8"], "A", radius=0.37, direction="top", color=ACCEPT_EDGE)

    # Panel 2: Minimal 8-state DFA
    ax2 = fig.add_subplot(gs[1])
    ax2.set_xlim(-1.4, 15.2)
    ax2.set_ylim(-2.35, 2.55)
    ax2.axis("off")
    ax2.text(
        6.9,
        2.32,
        "Application 3 (Part B): Minimal 8-State Email DFA (Subset Construction + Partition Refinement)",
        ha="center",
        va="center",
        fontsize=11.5,
        fontweight="bold",
        color=NAVY,
    )

    dfa_pos = {
        "m0": (0.0, 0.45),
        "m1": (2.3, 0.45),
        "m2": (4.7, 0.45),
        "m3": (7.3, 0.45),
        "m4": (9.9, 1.05),
        "m5": (12.2, 1.05),
        "m6": (14.2, 0.45),
        "q_trap": (7.3, -1.65),
    }
    for st, pos in dfa_pos.items():
        draw_state(
            ax2,
            *pos,
            st,
            radius=0.38,
            initial=(st == "m0"),
            accepting=(st == "m6"),
            trap=(st == "q_trap"),
        )

    draw_edge(ax2, dfa_pos["m0"], dfa_pos["m1"], "A, D", r1=0.38, r2=0.38, rad=-0.16, label_pos=(1.15, 0.78), color=BLUE)
    draw_edge(ax2, dfa_pos["m1"], dfa_pos["m0"], "DOT, HYP, UND", r1=0.38, r2=0.38, rad=-0.22, label_pos=(1.15, -0.02), fontsize=7.4)
    draw_self_loop(ax2, *dfa_pos["m1"], "A, D", radius=0.38, direction="top", color=BLUE)
    draw_edge(ax2, dfa_pos["m1"], dfa_pos["m2"], "AT", r1=0.38, r2=0.38, label_pos=(3.5, 0.65), color=NAVY)
    draw_edge(ax2, dfa_pos["m2"], dfa_pos["m3"], "A, D", r1=0.38, r2=0.38, rad=-0.16, label_pos=(6.0, 0.78), color=BLUE)
    draw_edge(ax2, dfa_pos["m3"], dfa_pos["m2"], "HYP", r1=0.38, r2=0.38, rad=-0.22, label_pos=(6.0, -0.02), fontsize=7.6)
    draw_self_loop(ax2, *dfa_pos["m3"], "A, D", radius=0.38, direction="top", color=BLUE)

    draw_edge(ax2, dfa_pos["m3"], dfa_pos["m4"], "DOT", r1=0.38, r2=0.38, label_pos=(8.55, 0.92), color=NAVY)
    draw_edge(ax2, dfa_pos["m4"], dfa_pos["m3"], "D", r1=0.38, r2=0.38, rad=0.30, label_pos=(8.85, 0.38), fontsize=7.8)
    draw_edge(ax2, dfa_pos["m4"], dfa_pos["m5"], "A", r1=0.38, r2=0.38, label_pos=(11.05, 1.24), color=ACCEPT_EDGE)
    draw_edge(ax2, dfa_pos["m5"], dfa_pos["m6"], "A", r1=0.38, r2=0.38, label_pos=(13.35, 0.92), color=ACCEPT_EDGE)
    draw_self_loop(ax2, *dfa_pos["m6"], "A", radius=0.38, direction="top", color=ACCEPT_EDGE)

    # Clean back-edges from m5 and m6: positive rad curves UP when going left-to-right,
    # and negative rad curves DOWN when going right-to-left.
    draw_edge(ax2, dfa_pos["m5"], dfa_pos["m4"], "DOT", r1=0.38, r2=0.38, rad=0.42, label_pos=(11.05, 1.56), fontsize=7.4)
    draw_edge(ax2, dfa_pos["m6"], dfa_pos["m4"], "DOT", r1=0.38, r2=0.38, rad=0.45, label_pos=(12.30, 1.92), fontsize=7.4)
    draw_edge(ax2, dfa_pos["m5"], dfa_pos["m3"], "D", r1=0.38, r2=0.38, rad=-0.18, label_pos=(9.85, 0.48), fontsize=7.5)
    draw_edge(ax2, dfa_pos["m6"], dfa_pos["m3"], "D", r1=0.38, r2=0.38, rad=-0.22, label_pos=(11.15, -0.10), fontsize=7.5)
    draw_edge(ax2, dfa_pos["m5"], dfa_pos["m2"], "HYP", r1=0.38, r2=0.38, rad=-0.26, label_pos=(8.85, -0.35), fontsize=7.4)
    draw_edge(ax2, dfa_pos["m6"], dfa_pos["m2"], "HYP", r1=0.38, r2=0.38, rad=-0.32, label_pos=(10.25, -0.78), fontsize=7.4)

    # Trap edges
    draw_edge(ax2, dfa_pos["m3"], dfa_pos["q_trap"], "AT, UND, OTHER", r1=0.38, r2=0.38, label_pos=(7.30, -0.62), fontsize=7.3, color=TRAP_EDGE)
    draw_edge(ax2, dfa_pos["m0"], dfa_pos["q_trap"], "else", r1=0.38, r2=0.38, rad=0.18, label_pos=(3.1, -1.08), fontsize=7.4, color=TRAP_EDGE)
    draw_edge(ax2, dfa_pos["m2"], dfa_pos["q_trap"], "else", r1=0.38, r2=0.38, rad=0.08, label_pos=(5.65, -0.82), fontsize=7.4, color=TRAP_EDGE)
    draw_self_loop(ax2, *dfa_pos["q_trap"], "Σ", radius=0.38, direction="bottom", color=TRAP_EDGE)
    ax2.text(
        11.6,
        -1.65,
        "All remaining unlabelled transitions (e.g. OTHER, invalid DOT/HYP/UND/AT)\n"
        "route deterministically to the sink state q_trap (see complete table below).",
        ha="center",
        va="center",
        fontsize=8.0,
        color=TRAP_EDGE,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="#FEF2F2", edgecolor=TRAP_EDGE, linewidth=0.8),
    )

    # Panel 3: Minimal DFA Transition Table
    ax3 = fig.add_subplot(gs[2])
    ax3.axis("off")
    col_labels = ["Minimal State", "A", "D", "DOT (.)", "HYP (-)", "UND (_)", "AT (@)", "OTHER"]
    table_data = [
        ["-> m0", "m1", "m1", "q_trap", "q_trap", "q_trap", "q_trap", "q_trap"],
        ["m1", "m1", "m1", "m0", "m0", "m0", "m2", "q_trap"],
        ["m2", "m3", "m3", "q_trap", "q_trap", "q_trap", "q_trap", "q_trap"],
        ["m3", "m3", "m3", "m4", "m2", "q_trap", "q_trap", "q_trap"],
        ["m4", "m5", "m3", "q_trap", "q_trap", "q_trap", "q_trap", "q_trap"],
        ["m5", "m6", "m3", "m4", "m2", "q_trap", "q_trap", "q_trap"],
        ["* m6", "m6", "m3", "m4", "m2", "q_trap", "q_trap", "q_trap"],
        ["q_trap", "q_trap", "q_trap", "q_trap", "q_trap", "q_trap", "q_trap", "q_trap"],
    ]
    tbl = ax3.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.3)
    tbl.scale(1.0, 1.32)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(BORDER)
        if r == 0:
            cell.set_facecolor(NAVY)
            cell.set_text_props(color="white", fontweight="bold")
        elif r == 7:
            cell.set_facecolor("#F0FDF4")
        elif r == 8:
            cell.set_facecolor("#FEF2F2")
        else:
            cell.set_facecolor("#F8FAFC" if r % 2 == 0 else "white")

    out_path = OUT_DIR / "email_automaton.png"
    fig.savefig(out_path, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return out_path


def main() -> None:
    p1 = generate_pin_diagram()
    p2 = generate_password_diagram()
    p3 = generate_email_diagram()
    print("Generated diagrams:")
    for p in (p1, p2, p3):
        print(f" - {p} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
