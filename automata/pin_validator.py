"""Application 1: ATM PIN Verification System using a Deterministic Finite Automaton.

Formal Model:
    M_PIN = (Q, Sigma, delta, q0, F)
    Q     = {q0, q1, q2, q3, q4, q_trap}
    Sigma = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    q0    = q0 (0 digits read)
    F     = {q4} (exactly 4 valid digits read)
    L_PIN = {w in Sigma* : |w| = 4}

Any character outside Sigma (letters, spaces, punctuation, symbols) or any
5th+ digit transitions permanently into the rejecting sink state q_trap.
"""

from __future__ import annotations

from typing import Dict, Set, Tuple

from automata.dfa import DFA, ValidationResult


PIN_STATES: Tuple[str, ...] = ("q0", "q1", "q2", "q3", "q4", "q_trap")
PIN_ALPHABET: Tuple[str, ...] = tuple("0123456789")

PIN_STATE_DESCRIPTIONS: Dict[str, str] = {
    "q0": "Initial state: 0 valid digits processed",
    "q1": "1 valid numeric digit processed",
    "q2": "2 valid numeric digits processed",
    "q3": "3 valid numeric digits processed",
    "q4": "Accepting state: exactly 4 numeric digits processed",
    "q_trap": "Trap state: length > 4 or non-numeric character outside Sigma",
}


def build_pin_dfa() -> DFA:
    """Construct and return the complete 6-state ATM PIN DFA."""
    transitions: Dict[Tuple[str, str], str] = {}
    for digit in PIN_ALPHABET:
        transitions[("q0", digit)] = "q1"
        transitions[("q1", digit)] = "q2"
        transitions[("q2", digit)] = "q3"
        transitions[("q3", digit)] = "q4"
        transitions[("q4", digit)] = "q_trap"
        transitions[("q_trap", digit)] = "q_trap"

    return DFA(
        name="ATM PIN Validator DFA",
        states=PIN_STATES,
        alphabet=PIN_ALPHABET,
        transitions=transitions,
        initial_state="q0",
        final_states={"q4"},
        trap_state="q_trap",
        classifier=None,
        state_descriptions=PIN_STATE_DESCRIPTIONS,
        symbol_descriptions={d: f"Numeric digit '{d}'" for d in PIN_ALPHABET},
    )


PIN_DFA: DFA = build_pin_dfa()


def validate_pin(pin_input: str) -> ValidationResult:
    """Validate an ATM PIN candidate string against M_PIN."""
    return PIN_DFA.trace(pin_input)


def check_registered_pin_semantic(
    pin_input: str, registered_pins: Set[str]
) -> Tuple[bool, str]:
    """Demonstrate the boundary between DFA syntax validation and bank DB lookup.

    Step 1 (Syntax): Run M_PIN to confirm w in {0..9}^4.
    Step 2 (Semantics): Compare against registered PIN records (outside FA scope).
    """
    syntax_result = validate_pin(pin_input)
    if not syntax_result.accepted:
        return (
            False,
            f"Rejected at syntax stage ({syntax_result.reason}). "
            "Bank database lookup skipped.",
        )
    if pin_input in registered_pins:
        return True, "Syntax accepted by DFA and PIN matched registered record."
    return (
        False,
        "Syntax accepted by DFA (4 digits), but PIN does not match the "
        "registered bank record (semantic failure).",
    )
