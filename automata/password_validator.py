"""Application 2: Password Strength & Format Validator using Product DFA Construction.

Policy (Regular Language L_PWD over Sigma = {U, L, D, S, O}):
    1. Length between 8 and 16 characters inclusive (8 <= |w| <= 16).
    2. At least one Uppercase letter (U: A-Z).
    3. At least one Lowercase letter (L: a-z).
    4. At least one Digit (D: 0-9).
    5. At least one Special character (S: printable ASCII punctuation).
    6. No Other/disallowed characters (O: spaces, control chars, non-ASCII).

Formal Construction:
    L_PWD = L_len ∩ L_U ∩ L_L ∩ L_D ∩ L_S
    Since regular languages are closed under intersection, we build five
    modular component DFAs and combine them via formal Cartesian product
    construction (automata.dfa.product_dfa) into a single deterministic
    automaton, and also derive its Hopcroft/Moore-minimized equivalent.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from automata.dfa import DFA, ValidationResult, product_dfa


SPECIAL_CHARACTERS: str = "!@#$%^&*()-_=+[]{};:'\",.<>?/\\|`~"
PASSWORD_ALPHABET: Tuple[str, ...] = ("U", "L", "D", "S", "O")

SYMBOL_DESCRIPTIONS: Dict[str, str] = {
    "U": "Uppercase letter (A-Z)",
    "L": "Lowercase letter (a-z)",
    "D": "Numeric digit (0-9)",
    "S": f"Special character in {SPECIAL_CHARACTERS}",
    "O": "Other / disallowed character (whitespace, control, non-ASCII)",
}


def classify_password_char(ch: str) -> str:
    """Classify a single character into {U, L, D, S, O}."""
    if len(ch) != 1:
        return "O"
    if "A" <= ch <= "Z":
        return "U"
    if "a" <= ch <= "z":
        return "L"
    if "0" <= ch <= "9":
        return "D"
    if ch in SPECIAL_CHARACTERS:
        return "S"
    return "O"


def _build_length_and_allowed_dfa(min_len: int = 8, max_len: int = 16) -> DFA:
    """Component DFA accepting strings of length [min_len, max_len] with no 'O'."""
    states = [str(i) for i in range(max_len + 1)] + ["len_trap"]
    transitions: Dict[Tuple[str, str], str] = {}
    allowed = ("U", "L", "D", "S")

    for i in range(max_len + 1):
        s = str(i)
        transitions[(s, "O")] = "len_trap"
        nxt = str(i + 1) if i < max_len else "len_trap"
        for sym in allowed:
            transitions[(s, sym)] = nxt

    for sym in PASSWORD_ALPHABET:
        transitions[("len_trap", sym)] = "len_trap"

    finals = {str(i) for i in range(min_len, max_len + 1)}
    return DFA(
        name="Password Length & Allowed-Char DFA",
        states=states,
        alphabet=PASSWORD_ALPHABET,
        transitions=transitions,
        initial_state="0",
        final_states=finals,
        trap_state="len_trap",
        classifier=classify_password_char,
        symbol_descriptions=SYMBOL_DESCRIPTIONS,
    )


def _build_contains_class_dfa(target_sym: str, prefix: str) -> DFA:
    """2-state component DFA accepting iff target_sym appears at least once."""
    s0 = f"{prefix}0"
    s1 = f"{prefix}1"
    transitions: Dict[Tuple[str, str], str] = {}
    for sym in PASSWORD_ALPHABET:
        transitions[(s0, sym)] = s1 if sym == target_sym else s0
        transitions[(s1, sym)] = s1

    return DFA(
        name=f"Contains-{target_sym} DFA",
        states={s0, s1},
        alphabet=PASSWORD_ALPHABET,
        transitions=transitions,
        initial_state=s0,
        final_states={s1},
        trap_state=None,
        classifier=classify_password_char,
        symbol_descriptions=SYMBOL_DESCRIPTIONS,
    )


def build_password_components() -> List[DFA]:
    """Return the 5 component DFAs [M_len, M_U, M_L, M_D, M_S]."""
    return [
        _build_length_and_allowed_dfa(8, 16),
        _build_contains_class_dfa("U", "U"),
        _build_contains_class_dfa("L", "L"),
        _build_contains_class_dfa("D", "D"),
        _build_contains_class_dfa("S", "S"),
    ]


def build_password_dfa() -> DFA:
    """Construct the reachable product DFA for the full password policy."""
    components = build_password_components()
    return product_dfa(
        components,
        name="Password Policy Product DFA",
        mode="intersection",
        trap_name="q_trap",
        classifier=classify_password_char,
    )


PASSWORD_COMPONENTS: List[DFA] = build_password_components()
PASSWORD_DFA: DFA = build_password_dfa()
PASSWORD_MINIMAL_DFA: DFA = PASSWORD_DFA.minimize(state_prefix="pm")


def validate_password(password: str) -> ValidationResult:
    """Validate a candidate password against PASSWORD_DFA and enrich feedback."""
    result = PASSWORD_DFA.trace(password)
    if not result.accepted:
        diagnostics: List[str] = []
        if len(password) < 8:
            diagnostics.append(f"length is {len(password)} (< 8)")
        elif len(password) > 16:
            diagnostics.append(f"length is {len(password)} (> 16)")
        classes_seen = {classify_password_char(ch) for ch in password}
        if "O" in classes_seen:
            diagnostics.append("contains disallowed character(s) of class O")
        for cls_key, label in (
            ("U", "uppercase letter"),
            ("L", "lowercase letter"),
            ("D", "digit"),
            ("S", "special character"),
        ):
            if cls_key not in classes_seen:
                diagnostics.append(f"missing {label} ({cls_key})")
        if diagnostics:
            result.reason = (
                f"Ended in '{result.final_state}' (REJECTED): "
                + "; ".join(diagnostics)
                + "."
            )
    else:
        result.reason = (
            f"Ended in accepting product state '{result.final_state}' "
            f"(length={len(password)}, all four classes U/L/D/S satisfied)."
        )
    return result


def check_password_authentication_semantic(
    password: str, stored_passwords: Set[str]
) -> Tuple[bool, str]:
    """Illustrate format validation (DFA) vs. credential authentication (backend)."""
    syntax_res = validate_password(password)
    if not syntax_res.accepted:
        return (
            False,
            f"Rejected at syntax stage: {syntax_res.reason} "
            "Authentication hash check not executed.",
        )
    if password in stored_passwords:
        return (
            True,
            "Format accepted by DFA and password matched stored credential.",
        )
    return (
        False,
        "Format accepted by DFA (strong policy met), but password does not "
        "match the user's stored account credential (semantic mismatch).",
    )
