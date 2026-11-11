"""Interactive Streamlit Web Application:
Finite Automata-Based Real-Time Input Validation System

Course: 21CSC301T - Formal Language and Automata (CLA-2 Task 2)
SRM Institute of Science and Technology, Tiruchirappalli
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Set

import pandas as pd
import streamlit as st

from automata.email_validator import (
    EMAIL_DFA,
    EMAIL_NFA,
    EMAIL_SUBSET_DFA,
    check_email_deliverability_semantic,
    validate_email,
    validate_email_nfa,
)
from automata.password_validator import (
    PASSWORD_COMPONENTS,
    PASSWORD_DFA,
    PASSWORD_MINIMAL_DFA,
    check_password_authentication_semantic,
    classify_password_char,
    validate_password,
)
from automata.pin_validator import (
    PIN_DFA,
    check_registered_pin_semantic,
    validate_pin,
)


BASE_DIR = Path(__file__).resolve().parent
DIAGRAMS_DIR = BASE_DIR / "diagrams"


st.set_page_config(
    page_title="Finite Automata Real-Time Validation System",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Academic Blue & White Theme CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    section[data-testid="stSidebar"] {
        background-color: #0F2C59;
        color: #FFFFFF;
    }
    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #E2E8F0 !important;
        font-weight: 500;
    }
    .academic-header {
        background: linear-gradient(135deg, #0F2C59 0%, #1E40AF 100%);
        color: #FFFFFF;
        padding: 1.35rem 1.75rem;
        border-radius: 10px;
        margin-bottom: 1.25rem;
        box-shadow: 0 2px 8px rgba(15, 44, 89, 0.15);
    }
    .academic-header h1 {
        color: #FFFFFF;
        font-size: 1.65rem;
        margin: 0 0 0.25rem 0;
        font-weight: 700;
    }
    .academic-header p {
        color: #DBEAFE;
        font-size: 0.92rem;
        margin: 0;
    }
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 4px solid #1D4ED8;
        border-radius: 8px;
        padding: 1rem 1.1rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .metric-card h4 {
        color: #0F2C59;
        margin: 0 0 0.35rem 0;
        font-size: 1.0rem;
    }
    .metric-card p {
        color: #334155;
        margin: 0;
        font-size: 0.88rem;
    }
    .status-accepted {
        background-color: #DCFCE7;
        border: 1.5px solid #15803D;
        color: #14532D;
        padding: 0.9rem 1.15rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.6rem 0;
    }
    .status-rejected {
        background-color: #FEE2E2;
        border: 1.5px solid #B91C1C;
        color: #7F1D1D;
        padding: 0.9rem 1.15rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.6rem 0;
    }
    .formal-box {
        background-color: #EFF6FF;
        border-left: 4px solid #1D4ED8;
        padding: 0.85rem 1rem;
        border-radius: 0 6px 6px 0;
        color: #0F172A;
        font-size: 0.9rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_header() -> None:
    st.markdown(
        """
        <div class="academic-header">
            <h1>Finite Automata-Based Real-Time Input Validation System</h1>
            <p>21CSC301T – Formal Language and Automata &nbsp;|&nbsp; CLA-2 Task 2 &nbsp;|&nbsp;
            Department of AIML, SRM Institute of Science and Technology, Tiruchirappalli</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _node_colors(
    state: str,
    final_states: Set[str],
    trap_state: str | None,
    active_states: Set[str],
    visited_states: Set[str],
) -> tuple[str, str, str]:
    """Return (fill, stroke, stroke_width) for live SVG automaton highlighting."""
    if state in active_states:
        if state in final_states:
            return ("#BBF7D0", "#15803D", "3.5")
        if state == trap_state:
            return ("#FECACA", "#B91C1C", "3.5")
        return ("#FDE68A", "#D97706", "3.5")
    if state in visited_states:
        return ("#DBEAFE", "#1D4ED8", "2.4")
    if state in final_states:
        return ("#DCFCE7", "#15803D", "2.0")
    if state == trap_state:
        return ("#FEE2E2", "#B91C1C", "2.0")
    return ("#F8FAFC", "#0F2C59", "2.0")


def render_pin_live_svg(active_state: str, visited: Set[str]) -> str:
    """Render an inline SVG of the 6-state ATM PIN DFA with live state highlight."""
    pos = {
        "q0": (95, 75),
        "q1": (235, 75),
        "q2": (375, 75),
        "q3": (515, 75),
        "q4": (655, 75),
        "q_trap": (375, 195),
    }
    lines = [
        '<svg viewBox="0 0 760 260" width="100%" xmlns="http://www.w3.org/2000/svg" '
        'style="background:#FFFFFF;border:1px solid #CBD5E1;border-radius:8px;">',
        '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#334155"/></marker></defs>',
        # Start arrow
        '<line x1="25" y1="75" x2="65" y2="75" stroke="#0F2C59" stroke-width="2.2" marker-end="url(#arr)"/>',
        '<text x="20" y="63" font-size="11" fill="#0F2C59" font-style="italic">start</text>',
    ]
    # Forward digit edges
    for a, b in [("q0", "q1"), ("q1", "q2"), ("q2", "q3"), ("q3", "q4")]:
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        lines.append(
            f'<line x1="{x1+28}" y1="{y1}" x2="{x2-30}" y2="{y2}" '
            'stroke="#1D4ED8" stroke-width="2" marker-end="url(#arr)"/>'
        )
        lines.append(
            f'<text x="{(x1+x2)//2}" y="62" text-anchor="middle" font-size="11" '
            'font-weight="bold" fill="#1D4ED8">0-9</text>'
        )
    # Edges to trap
    for s in ("q0", "q1", "q2", "q3", "q4"):
        x1, y1 = pos[s]
        xt, yt = pos["q_trap"]
        lbl = "0-9, ∉Σ" if s == "q4" else "∉Σ"
        lines.append(
            f'<line x1="{x1}" y1="{y1+28}" x2="{xt}" y2="{yt-30}" '
            'stroke="#DC2626" stroke-width="1.3" stroke-dasharray="4,3" marker-end="url(#arr)"/>'
        )
        lines.append(
            f'<text x="{(x1+xt)//2 + (14 if s=="q4" else -10)}" y="{(y1+yt)//2}" '
            f'text-anchor="middle" font-size="10" fill="#B91C1C">{lbl}</text>'
        )
    # Trap self-loop
    lines.append(
        '<path d="M 358 220 C 345 252, 405 252, 392 220" fill="none" '
        'stroke="#B91C1C" stroke-width="1.6" marker-end="url(#arr)"/>'
    )
    lines.append(
        '<text x="375" y="253" text-anchor="middle" font-size="10" fill="#B91C1C">0-9, ∉Σ</text>'
    )

    for state, (cx, cy) in pos.items():
        fill, stroke, sw = _node_colors(
            state, {"q4"}, "q_trap", {active_state}, visited
        )
        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="27" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )
        if state == "q4":
            lines.append(
                f'<circle cx="{cx}" cy="{cy}" r="21" fill="none" stroke="{stroke}" stroke-width="1.8"/>'
            )
        lines.append(
            f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="13" '
            'font-weight="bold" fill="#0F172A">'
            f"{state}</text>"
        )
    lines.append("</svg>")
    return "\n".join(lines)


def render_email_live_svg(active_state: str, visited: Set[str]) -> str:
    """Render an inline SVG of the Minimal 8-state Email DFA with live state highlight."""
    pos = {
        "m0": (70, 95),
        "m1": (185, 95),
        "m2": (300, 95),
        "m3": (415, 95),
        "m4": (535, 55),
        "m5": (650, 55),
        "m6": (765, 95),
        "q_trap": (415, 225),
    }
    lines = [
        '<svg viewBox="0 0 835 280" width="100%" xmlns="http://www.w3.org/2000/svg" '
        'style="background:#FFFFFF;border:1px solid #CBD5E1;border-radius:8px;">',
        '<defs><marker id="arrE" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#334155"/></marker></defs>',
        '<line x1="12" y1="95" x2="42" y2="95" stroke="#0F2C59" stroke-width="2.2" marker-end="url(#arrE)"/>',
    ]
    edges = [
        ("m0", "m1", "A, D", "#1D4ED8", -12),
        ("m1", "m2", "AT", "#0F2C59", -12),
        ("m2", "m3", "A, D", "#1D4ED8", -12),
        ("m3", "m4", "DOT", "#0F2C59", -12),
        ("m4", "m5", "A", "#15803D", -12),
        ("m5", "m6", "A", "#15803D", -12),
    ]
    for a, b, lbl, col, dy in edges:
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        lines.append(
            f'<line x1="{x1+24}" y1="{y1}" x2="{x2-26}" y2="{y2}" '
            f'stroke="{col}" stroke-width="2" marker-end="url(#arrE)"/>'
        )
        lines.append(
            f'<text x="{(x1+x2)//2}" y="{(y1+y2)//2 + dy}" text-anchor="middle" '
            f'font-size="10.5" font-weight="bold" fill="{col}">{lbl}</text>'
        )

    # Back edges & self-loops
    lines.extend([
        '<path d="M 173 118 Q 127 150 82 118" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arrE)"/>',
        '<text x="127" y="148" text-anchor="middle" font-size="9.5" fill="#475569">DOT,HYP,UND</text>',
        '<path d="M 403 118 Q 357 150 312 118" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arrE)"/>',
        '<text x="357" y="148" text-anchor="middle" font-size="9.5" fill="#475569">HYP</text>',
        '<path d="M 172 72 C 160 35, 210 35, 198 72" fill="none" stroke="#1D4ED8" stroke-width="1.5" marker-end="url(#arrE)"/>',
        '<text x="185" y="34" text-anchor="middle" font-size="10" fill="#1D4ED8">A, D</text>',
        '<path d="M 402 72 C 390 35, 440 35, 428 72" fill="none" stroke="#1D4ED8" stroke-width="1.5" marker-end="url(#arrE)"/>',
        '<text x="415" y="34" text-anchor="middle" font-size="10" fill="#1D4ED8">A, D</text>',
        '<path d="M 752 72 C 740 35, 790 35, 778 72" fill="none" stroke="#15803D" stroke-width="1.5" marker-end="url(#arrE)"/>',
        '<text x="765" y="34" text-anchor="middle" font-size="10" fill="#15803D">A</text>',
        '<line x1="415" y1="122" x2="415" y2="195" stroke="#B91C1C" stroke-width="1.4" stroke-dasharray="4,3" marker-end="url(#arrE)"/>',
        '<text x="475" y="170" text-anchor="middle" font-size="9.5" fill="#B91C1C">invalid / OTHER -> q_trap</text>',
    ])

    for state, (cx, cy) in pos.items():
        fill, stroke, sw = _node_colors(
            state, {"m6"}, "q_trap", {active_state}, visited
        )
        lines.append(
            f'<circle cx="{cx}" cy="{cy}" r="25" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )
        if state == "m6":
            lines.append(
                f'<circle cx="{cx}" cy="{cy}" r="19" fill="none" stroke="{stroke}" stroke-width="1.8"/>'
            )
        lines.append(
            f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="12.5" '
            f'font-weight="bold" fill="#0F172A">{state}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def page_dashboard() -> None:
    st.subheader("Project Dashboard & Formal Automata Overview")
    st.markdown(
        """
        <div class="formal-box">
        <b>Objective:</b> Design, formalize, and implement deterministic and nondeterministic finite automata
        for real-time syntactic input validation across three industry-standard workflows:
        <b>ATM PIN Verification</b>, <b>Password Policy Validation</b>, and <b>Email Syntax Checking</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>1. ATM PIN Validator (DFA)</h4>
                <p><b>Model:</b> Complete 6-state DFA<br>
                <b>States:</b> {len(PIN_DFA.states)} (q0..q4, q_trap)<br>
                <b>Alphabet:</b> {{0..9}} (non-digits -> q_trap)<br>
                <b>Language:</b> {{w ∈ Σ* : |w| = 4}}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>2. Password Policy (Product DFA)</h4>
                <p><b>Model:</b> Intersection of 5 DFAs<br>
                <b>Component States:</b> 26 total (18+2+2+2+2)<br>
                <b>Product DFA:</b> {len(PASSWORD_DFA.states)} states<br>
                <b>Minimal DFA:</b> {len(PASSWORD_MINIMAL_DFA.states)} states</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>3. Email Syntax (NFA → Minimal DFA)</h4>
                <p><b>Model:</b> 9-state NFA → Subset Construction<br>
                <b>Subset DFA:</b> {len(EMAIL_SUBSET_DFA.states)} states<br>
                <b>Minimal DFA:</b> {len(EMAIL_DFA.states)} states<br>
                <b>Alphabet Classes:</b> {{A, D, DOT, HYP, UND, AT, OTHER}}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Comparative Summary of Finite Automata Models")
    summary_df = pd.DataFrame(
        [
            {
                "Application": "ATM PIN Verification",
                "Formal Model": "Direct Complete DFA",
                "States (|Q|)": len(PIN_DFA.states),
                "Accepting States (|F|)": len(PIN_DFA.final_states),
                "Alphabet": "{0..9} + invalid trap",
                "Memory Requirement": "Bounded count 0..4",
                "Beyond FA (Semantics)": "Bank DB / HSM PIN hash match",
            },
            {
                "Application": "Password Strength & Format",
                "Formal Model": "Product DFA + Minimization",
                "States (|Q|)": f"{len(PASSWORD_DFA.states)} (min {len(PASSWORD_MINIMAL_DFA.states)})",
                "Accepting States (|F|)": len(PASSWORD_DFA.final_states),
                "Alphabet": "{U, L, D, S, O}",
                "Memory Requirement": "Length 0..16 × 4-bit class mask",
                "Beyond FA (Semantics)": "Account hash & breach-list check",
            },
            {
                "Application": "Email Format Validation",
                "Formal Model": "9-State NFA -> 8-State Min DFA",
                "States (|Q|)": f"NFA {len(EMAIL_NFA.states)} / DFA {len(EMAIL_DFA.states)}",
                "Accepting States (|F|)": len(EMAIL_DFA.final_states),
                "Alphabet": "{A, D, DOT, HYP, UND, AT, OTHER}",
                "Memory Requirement": "Section phase & separator guard",
                "Beyond FA (Semantics)": "DNS MX lookup & SMTP mailbox",
            },
        ]
    )
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.markdown("### Generated Formal Automata Diagrams")
    tab1, tab2, tab3 = st.tabs(["ATM PIN DFA", "Password Product DFA", "Email NFA & Minimal DFA"])
    with tab1:
        if (DIAGRAMS_DIR / "pin_dfa.png").exists():
            st.image(str(DIAGRAMS_DIR / "pin_dfa.png"), use_container_width=True)
    with tab2:
        if (DIAGRAMS_DIR / "password_dfa.png").exists():
            st.image(str(DIAGRAMS_DIR / "password_dfa.png"), use_container_width=True)
    with tab3:
        if (DIAGRAMS_DIR / "email_automaton.png").exists():
            st.image(str(DIAGRAMS_DIR / "email_automaton.png"), use_container_width=True)


def _display_trace_and_result(res) -> None:
    if res.accepted:
        st.markdown(
            f'<div class="status-accepted">ACCEPTED &nbsp;|&nbsp; Final State: <code>{res.final_state}</code><br>'
            f'<span style="font-weight:400;font-size:0.9rem;">{res.reason}</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="status-rejected">REJECTED &nbsp;|&nbsp; Final State: <code>{res.final_state}</code><br>'
            f'<span style="font-weight:400;font-size:0.9rem;">{res.reason}</span></div>',
            unsafe_allow_html=True,
        )

    if res.steps:
        df_steps = pd.DataFrame(
            [
                {
                    "Step": s.step,
                    "Current State": s.current_state,
                    "Raw Char": repr(s.raw_char),
                    "Symbol": s.symbol,
                    "Next State": s.next_state,
                    "Trap?": "Yes" if s.is_trap else "No",
                    "Transition Note": s.note,
                }
                for s in res.steps
            ]
        )
        st.dataframe(df_steps, use_container_width=True, hide_index=True)
    else:
        st.info("Empty string (ε): 0 transitions executed; evaluated directly at initial state.")


def page_pin_validator() -> None:
    st.subheader("Application 1: ATM PIN Verification System (DFA)")
    st.markdown(
        """
        <div class="formal-box">
        <b>Formal Model:</b> <code>M_PIN = ({q0, q1, q2, q3, q4, q_trap}, {0..9}, δ, q0, {q4})</code> &nbsp;|&nbsp;
        <b>Language:</b> <code>L_PIN = {w ∈ Σ* : |w| = 4}</code>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    samples = {
        "Accepted: 4821": "4821",
        "Accepted: 0000": "0000",
        "Rejected (3 digits): 482": "482",
        "Rejected (5 digits): 48219": "48219",
        "Rejected (letter): 48a1": "48a1",
        "Rejected (space): 12 34": "12 34",
        "Rejected (empty ε)": "",
    }
    col_in, col_btn = st.columns([2, 1])
    with col_btn:
        chosen = st.selectbox("Quick Sample Input", list(samples.keys()))
        if st.button("Load Sample", key="pin_load"):
            st.session_state["pin_input"] = samples[chosen]
    with col_in:
        pin_val = st.text_input(
            "Enter ATM PIN Candidate:",
            value=st.session_state.get("pin_input", "4821"),
            key="pin_text",
        )

    res = validate_pin(pin_val)
    visited = {PIN_DFA.initial_state} | {s.next_state for s in res.steps}
    st.markdown("**Live Automaton State Highlight:**")
    st.markdown(render_pin_live_svg(res.final_state, visited), unsafe_allow_html=True)
    _display_trace_and_result(res)

    with st.expander("Syntax Validation vs. Bank Database Verification (Semantic Layer)"):
        registered = {"4821", "9375", "0042"}
        ok, msg = check_registered_pin_semantic(pin_val, registered)
        st.write(f"Simulated Registered Bank PINs: `{sorted(registered)}`")
        if ok:
            st.success(msg)
        else:
            st.warning(msg)

    with st.expander("Formal Transition Table & Diagram"):
        st.dataframe(pd.DataFrame(PIN_DFA.transition_table_rows()), use_container_width=True, hide_index=True)
        if (DIAGRAMS_DIR / "pin_dfa.png").exists():
            st.image(str(DIAGRAMS_DIR / "pin_dfa.png"), use_container_width=True)


def page_password_validator() -> None:
    st.subheader("Application 2: Password Strength & Format Validator (Product DFA)")
    st.markdown(
        """
        <div class="formal-box">
        <b>Policy:</b> 8–16 characters, ≥1 Uppercase (<code>U</code>), ≥1 Lowercase (<code>L</code>),
        ≥1 Digit (<code>D</code>), ≥1 Special (<code>S</code>), and no disallowed characters (<code>O</code>).<br>
        <b>Formal Construction:</b> <code>L_PWD = L_len ∩ L_U ∩ L_L ∩ L_D ∩ L_S</code> realized as a 225-state
        complete Product DFA (197 states after Hopcroft/Moore minimization).
        </div>
        """,
        unsafe_allow_html=True,
    )

    samples = {
        "Accepted (8-char boundary): Ab1!efgh": "Ab1!efgh",
        "Accepted (strong): Campus@2026": "Campus@2026",
        "Accepted (16-char boundary): K7$mNp2qR8vW!xZ4": "K7$mNp2qR8vW!xZ4",
        "Rejected (7 chars): Ab1!efg": "Ab1!efg",
        "Rejected (17 chars): Ab1!efghIjklMn0pQ": "Ab1!efghIjklMn0pQ",
        "Rejected (no uppercase): campus@2026": "campus@2026",
        "Rejected (no digit): Campus@Aiml": "Campus@Aiml",
        "Rejected (space -> O): Campus @2026": "Campus @2026",
    }
    col_in, col_btn = st.columns([2, 1])
    with col_btn:
        chosen = st.selectbox("Quick Sample Input", list(samples.keys()), key="pwd_sel")
        if st.button("Load Sample", key="pwd_load"):
            st.session_state["pwd_input"] = samples[chosen]
    with col_in:
        pwd_val = st.text_input(
            "Enter Password Candidate:",
            value=st.session_state.get("pwd_input", "Campus@2026"),
            key="pwd_text",
        )

    # Component DFA live status cards
    cols = st.columns(5)
    comp_labels = [
        ("Length (8–16, no O)", PASSWORD_COMPONENTS[0]),
        ("Uppercase (U)", PASSWORD_COMPONENTS[1]),
        ("Lowercase (L)", PASSWORD_COMPONENTS[2]),
        ("Digit (D)", PASSWORD_COMPONENTS[3]),
        ("Special (S)", PASSWORD_COMPONENTS[4]),
    ]
    for col, (title, comp_dfa) in zip(cols, comp_labels):
        comp_res = comp_dfa.trace(pwd_val)
        badge = "PASS" if comp_res.accepted else "FAIL"
        color = "#15803D" if comp_res.accepted else "#B91C1C"
        col.markdown(
            f'<div class="metric-card" style="border-top-color:{color};padding:0.65rem;">'
            f'<b>{title}</b><br><span style="color:{color};font-weight:700;">{badge}</span> '
            f'<code>{comp_res.final_state}</code></div>',
            unsafe_allow_html=True,
        )

    res = validate_password(pwd_val)
    _display_trace_and_result(res)

    with st.expander("Character Classification Breakdown & Authentication Boundary"):
        if pwd_val:
            cls_rows = [
                {"Index": i, "Character": repr(ch), "Class": classify_password_char(ch)}
                for i, ch in enumerate(pwd_val, start=1)
            ]
            st.dataframe(pd.DataFrame(cls_rows), use_container_width=True, hide_index=True)
        vault = {"Campus@2026", "K7$mNp2qR8vW!xZ4"}
        ok, msg = check_password_authentication_semantic(pwd_val, vault)
        if ok:
            st.success(msg)
        else:
            st.warning(msg)

    with st.expander("Product DFA Diagram & Architecture"):
        if (DIAGRAMS_DIR / "password_dfa.png").exists():
            st.image(str(DIAGRAMS_DIR / "password_dfa.png"), use_container_width=True)


def page_email_validator() -> None:
    st.subheader("Application 3: Email Format Validation System (NFA & Minimal DFA)")
    st.markdown(
        """
        <div class="formal-box">
        <b>Model:</b> 9-state NFA (<code>n0..n8</code>) branching nondeterministically on domain dots <code>'.'</code>
        to <code>{n3, n6}</code>, converted via subset construction to a 10-state DFA and minimized to an
        <b>8-state Minimal DFA</b> (<code>m0..m6, q_trap</code>). Enforces a practical subset of RFC 5322.
        </div>
        """,
        unsafe_allow_html=True,
    )

    samples = {
        "Accepted: student@srm.edu": "student@srm.edu",
        "Accepted (multi-level): aiml.lab_01@campus-1.edu.in": "aiml.lab_01@campus-1.edu.in",
        "Accepted (short): a@b.io": "a@b.io",
        "Rejected (no TLD): student@srm": "student@srm",
        "Rejected (double dot): stu..dent@srm.edu": "stu..dent@srm.edu",
        "Rejected (leading hyphen domain): student@-srm.edu": "student@-srm.edu",
        "Rejected (underscore in domain): student@srm_lab.edu": "student@srm_lab.edu",
        "Rejected (digit in TLD): student@srm.c0m": "student@srm.c0m",
        "Rejected (double @): student@@srm.edu": "student@@srm.edu",
    }
    col_in, col_btn = st.columns([2, 1])
    with col_btn:
        chosen = st.selectbox("Quick Sample Input", list(samples.keys()), key="email_sel")
        if st.button("Load Sample", key="email_load"):
            st.session_state["email_input"] = samples[chosen]
    with col_in:
        email_val = st.text_input(
            "Enter Email Candidate:",
            value=st.session_state.get("email_input", "aiml.lab_01@campus-1.edu.in"),
            key="email_text",
        )

    mode = st.radio(
        "Execution Engine:",
        ["Minimal 8-State DFA", "9-State NFA (Active State Sets)"],
        horizontal=True,
    )

    dfa_res = validate_email(email_val)
    visited = {EMAIL_DFA.initial_state} | {s.next_state for s in dfa_res.steps}
    st.markdown("**Live Minimal DFA State Highlight:**")
    st.markdown(render_email_live_svg(dfa_res.final_state, visited), unsafe_allow_html=True)

    if mode == "Minimal 8-State DFA":
        _display_trace_and_result(dfa_res)
    else:
        nfa_res = validate_email_nfa(email_val)
        if nfa_res.accepted:
            st.markdown(
                f'<div class="status-accepted">ACCEPTED (NFA) &nbsp;|&nbsp; Active Final Set: '
                f'<code>{{{", ".join(nfa_res.final_states)}}}</code><br>'
                f'<span style="font-weight:400;font-size:0.9rem;">{nfa_res.reason}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="status-rejected">REJECTED (NFA) &nbsp;|&nbsp; Active Final Set: '
                f'<code>{{{", ".join(nfa_res.final_states)}}}</code><br>'
                f'<span style="font-weight:400;font-size:0.9rem;">{nfa_res.reason}</span></div>',
                unsafe_allow_html=True,
            )
        if nfa_res.steps:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Step": s.step,
                            "Active NFA States": "{" + ", ".join(s.active_states) + "}",
                            "Raw Char": repr(s.raw_char),
                            "Symbol": s.symbol,
                            "Next NFA States": "{" + ", ".join(s.next_states) + "}",
                            "Transition Note": s.note,
                        }
                        for s in nfa_res.steps
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )

    with st.expander("Syntax Validation vs. Mailbox Existence (DNS/SMTP Layer)"):
        directory = {"student@srm.edu", "aiml.lab_01@campus-1.edu.in"}
        ok, msg = check_email_deliverability_semantic(email_val, directory)
        if ok:
            st.success(msg)
        else:
            st.warning(msg)

    with st.expander("Minimal DFA Transition Table & NFA/DFA Diagram"):
        ordered = ["m0", "m1", "m2", "m3", "m4", "m5", "m6", "q_trap"]
        st.dataframe(
            pd.DataFrame(EMAIL_DFA.transition_table_rows(ordered)),
            use_container_width=True,
            hide_index=True,
        )
        if (DIAGRAMS_DIR / "email_automaton.png").exists():
            st.image(str(DIAGRAMS_DIR / "email_automaton.png"), use_container_width=True)


def page_test_suite() -> None:
    st.subheader("Automated Sample Test Cases Verification")
    st.write(
        "Live execution of curated Accepted and Rejected test cases across all three automata."
    )

    suites = [
        (
            "Application 1: ATM PIN DFA",
            validate_pin,
            [
                ("4821", True, "4 valid digits -> q4"),
                ("0000", True, "4 zero digits -> q4"),
                ("9375", True, "4 valid digits -> q4"),
                ("1234", True, "4 sequential digits -> q4"),
                ("0042", True, "Zero-padded 4 digits -> q4"),
                ("482", False, "Length 3 < 4 -> ends in q3"),
                ("48219", False, "Length 5 > 4 -> q_trap"),
                ("48a1", False, "Non-digit 'a' -> q_trap"),
                ("12 34", False, "Space character -> q_trap"),
                ("", False, "Empty string ε -> stays in q0"),
            ],
        ),
        (
            "Application 2: Password Product DFA",
            validate_password,
            [
                ("Ab1!efgh", True, "8-char lower boundary with U,L,D,S"),
                ("Campus@2026", True, "11-char valid password"),
                ("Trichy#99Ai", True, "11-char mixed classes"),
                ("K7$mNp2qR8vW!xZ4", True, "16-char upper boundary"),
                ("9_ZeroOneA", True, "10-char with underscore special"),
                ("Ab1!efg", False, "Length 7 < 8"),
                ("Ab1!efghIjklMn0pQ", False, "Length 17 > 16 -> q_trap"),
                ("campus@2026", False, "Missing uppercase U"),
                ("Campus@Aiml", False, "Missing digit D"),
                ("Campus @2026", False, "Disallowed whitespace O -> q_trap"),
            ],
        ),
        (
            "Application 3: Email Minimal DFA",
            validate_email,
            [
                ("student@srm.edu", True, "Valid standard email"),
                ("aiml.lab_01@campus-1.edu.in", True, "Subdomain + 2-letter TLD"),
                ("a@b.io", True, "Minimal valid structure"),
                ("dept-chair@faculty.university.org", True, "Multi-label domain"),
                ("user_99@node2.cloud.info", True, "Underscore in local, digit in domain"),
                ("student@srm", False, "Missing domain dot and TLD"),
                ("stu..dent@srm.edu", False, "Consecutive dots in local"),
                ("student@-srm.edu", False, "Leading hyphen in domain"),
                ("student@srm_lab.edu", False, "Underscore in domain"),
                ("student@srm.c0m", False, "Digit in TLD"),
            ],
        ),
    ]

    for title, fn, cases in suites:
        st.markdown(f"#### {title}")
        rows = []
        passed_count = 0
        for inp, expected, explanation in cases:
            res = fn(inp)
            ok = res.accepted == expected
            if ok:
                passed_count += 1
            rows.append(
                {
                    "Input": repr(inp) if inp == "" else inp,
                    "Expected": "ACCEPTED" if expected else "REJECTED",
                    "Actual": res.status_label,
                    "Final State": res.final_state,
                    "Match": "PASS" if ok else "FAIL",
                    "Explanation": explanation,
                }
            )
        st.caption(f"Verified {passed_count}/{len(cases)} cases passed.")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def main() -> None:
    render_header()
    pages = [
        "Project Dashboard",
        "1. ATM PIN Validator",
        "2. Password Validator",
        "3. Email Validator",
        "Test Cases & Verification",
    ]
    qp_map = {
        "dashboard": 0,
        "pin": 1,
        "password": 2,
        "email": 3,
        "tests": 4,
    }
    default_idx = qp_map.get(st.query_params.get("page", "dashboard"), 0)

    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "Select Module",
            pages,
            index=default_idx,
        )
        st.markdown("---")
        st.markdown(
            "**Course:** 21CSC301T – FLA\n\n"
            "**Assessment:** CLA-2 Task 2\n\n"
            "**Faculty:** Dr. C. Gunasundari\n\n"
            "**SDG:** SDG 9 (Level 2)"
        )

    if page == "Project Dashboard":
        page_dashboard()
    elif page == "1. ATM PIN Validator":
        page_pin_validator()
    elif page == "2. Password Validator":
        page_password_validator()
    elif page == "3. Email Validator":
        page_email_validator()
    else:
        page_test_suite()


if __name__ == "__main__":
    main()
