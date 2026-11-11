"""Application 3: Email Format Validation System via NFA and Subset-Constructed DFA.

Practical Email Syntax Policy (Subset of RFC 5322 / RFC 1035):
    local-part @ domain-labels . tld
    - local-part:    alnum+ ( [._-] alnum+ )*
    - separator:     exactly one '@'
    - domain-label:  alnum ( alnum | '-' alnum )*   (underscores disallowed)
    - domain-dots:   at least one '.' separating domain labels and TLD;
                     no leading, trailing, or consecutive dots ('..')
    - TLD:           at least 2 ASCII letters ([A-Za-z]{2,})

Formal Construction:
    We first design a 9-state Nondeterministic Finite Automaton (NFA) M_EMAIL_NFA
    whose nondeterminism models the dot-lookahead ambiguity in the domain: upon
    reading '.', the NFA branches to either start another intermediate domain
    label (n3) or begin the final Top-Level Domain (n6).
    We then apply subset construction (to_dfa) and partition-refinement
    minimization (minimize) to obtain an equivalent complete minimal DFA.
"""

from __future__ import annotations

from typing import Dict, Iterable, Set, Tuple

from automata.dfa import DFA, ValidationResult
from automata.nfa import NFA, NFAValidationResult


EMAIL_ALPHABET: Tuple[str, ...] = (
    "A",      # ASCII Letter [A-Za-z]
    "D",      # ASCII Digit [0-9]
    "DOT",    # Period '.'
    "HYP",    # Hyphen '-'
    "UND",    # Underscore '_'
    "AT",     # At symbol '@'
    "OTHER",  # Any other character (invalid)
)

EMAIL_SYMBOL_DESCRIPTIONS: Dict[str, str] = {
    "A": "ASCII letter (A-Z, a-z)",
    "D": "ASCII digit (0-9)",
    "DOT": "Period '.'",
    "HYP": "Hyphen '-'",
    "UND": "Underscore '_' (allowed in local part only)",
    "AT": "At-sign '@'",
    "OTHER": "Other disallowed character (space, symbol, non-ASCII)",
}

EMAIL_NFA_STATES: Tuple[str, ...] = (
    "n0", "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8"
)

EMAIL_NFA_DESCRIPTIONS: Dict[str, str] = {
    "n0": "Initial state: expecting first alphanumeric char of local part",
    "n1": "Local part: reading alphanumeric characters",
    "n2": "Local part separator (., -, _) read; expecting alphanumeric next",
    "n3": "Domain label start: expecting alphanumeric start of a label",
    "n4": "Domain label body: valid label ending on alphanumeric",
    "n5": "Domain hyphen '-' read; expecting alphanumeric next",
    "n6": "TLD start (after guessed final dot): expecting 1st TLD letter",
    "n7": "TLD 1st letter read; expecting 2nd TLD letter",
    "n8": "Accepting state: TLD has >= 2 letters",
}


def classify_email_char(ch: str) -> str:
    """Classify a single character into EMAIL_ALPHABET."""
    if len(ch) != 1:
        return "OTHER"
    if ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
        return "A"
    if "0" <= ch <= "9":
        return "D"
    if ch == ".":
        return "DOT"
    if ch == "-":
        return "HYP"
    if ch == "_":
        return "UND"
    if ch == "@":
        return "AT"
    return "OTHER"


def build_email_nfa() -> NFA:
    """Construct the 9-state Email Format NFA."""
    transitions: Dict[Tuple[str, str], Iterable[str]] = {
        # Local part
        ("n0", "A"): {"n1"},
        ("n0", "D"): {"n1"},
        ("n1", "A"): {"n1"},
        ("n1", "D"): {"n1"},
        ("n1", "DOT"): {"n2"},
        ("n1", "HYP"): {"n2"},
        ("n1", "UND"): {"n2"},
        ("n1", "AT"): {"n3"},
        ("n2", "A"): {"n1"},
        ("n2", "D"): {"n1"},
        # Domain labels
        ("n3", "A"): {"n4"},
        ("n3", "D"): {"n4"},
        ("n4", "A"): {"n4"},
        ("n4", "D"): {"n4"},
        ("n4", "HYP"): {"n5"},
        # Nondeterministic branch on '.' in domain: next label (n3) or TLD (n6)
        ("n4", "DOT"): {"n3", "n6"},
        ("n5", "A"): {"n4"},
        ("n5", "D"): {"n4"},
        # Top-level domain (>= 2 ASCII letters)
        ("n6", "A"): {"n7"},
        ("n7", "A"): {"n8"},
        ("n8", "A"): {"n8"},
    }

    return NFA(
        name="Email Format NFA",
        states=EMAIL_NFA_STATES,
        alphabet=EMAIL_ALPHABET,
        transitions=transitions,
        initial_state="n0",
        final_states={"n8"},
        classifier=classify_email_char,
        state_descriptions=EMAIL_NFA_DESCRIPTIONS,
        symbol_descriptions=EMAIL_SYMBOL_DESCRIPTIONS,
    )


EMAIL_NFA: NFA = build_email_nfa()
EMAIL_SUBSET_DFA: DFA = EMAIL_NFA.to_dfa(
    name="Email Format Subset DFA", state_prefix="d", trap_name="q_trap"
)
EMAIL_DFA: DFA = EMAIL_SUBSET_DFA.minimize(state_prefix="m")
EMAIL_DFA.name = "Email Format Minimal DFA"


def validate_email(email: str) -> ValidationResult:
    """Validate an email candidate using the Minimal Email DFA."""
    return EMAIL_DFA.trace(email)


def validate_email_nfa(email: str) -> NFAValidationResult:
    """Validate an email candidate directly on the 9-state Email NFA."""
    return EMAIL_NFA.trace(email)


def check_email_deliverability_semantic(
    email: str, registered_accounts: Set[str]
) -> Tuple[bool, str]:
    """Illustrate syntax validation (FA) vs. domain/mailbox existence (DNS/SMTP)."""
    syntax_res = validate_email(email)
    if not syntax_res.accepted:
        return (
            False,
            f"Rejected at syntax stage ({syntax_res.reason}). "
            "DNS MX lookup and mailbox check skipped.",
        )
    if email.lower() in {acc.lower() for acc in registered_accounts}:
        return (
            True,
            "Syntax accepted by automaton and mailbox exists in simulated directory.",
        )
    return (
        False,
        "Syntax accepted by automaton, but no active mailbox exists for this "
        "address (semantic/DNS/SMTP verification failure).",
    )
