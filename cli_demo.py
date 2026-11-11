"""Command-line 5-minute demonstration script for Finite Automata Validators.

Usage:
    python cli_demo.py                # Prints summary tables + sample traces
    python cli_demo.py pin 4821       # Trace a custom ATM PIN
    python cli_demo.py password "Campus@2026"
    python cli_demo.py email "aiml.lab_01@campus-1.edu.in"
"""

from __future__ import annotations

import sys

from automata.email_validator import validate_email, validate_email_nfa
from automata.password_validator import validate_password
from automata.pin_validator import validate_pin


def print_dfa_trace(title: str, res) -> None:
    print(f"\n=== {title}: {res.input_string!r} ===")
    for step in res.steps:
        print(
            f"  {step.step:2d}. delta({step.current_state}, {step.raw_char!r} [{step.symbol}]) -> {step.next_state}"
        )
    print(f"  Result: {res.status_label} (final state: {res.final_state})")
    print(f"  Reason: {res.reason}")


def print_nfa_trace(title: str, res) -> None:
    print(f"\n=== {title}: {res.input_string!r} ===")
    for step in res.steps:
        cur = "{" + ", ".join(step.active_states) + "}"
        nxt = "{" + ", ".join(step.next_states) + "}"
        print(
            f"  {step.step:2d}. delta_N({cur}, {step.raw_char!r} [{step.symbol}]) -> {nxt}"
        )
    final_s = "{" + ", ".join(res.final_states) + "}"
    print(f"  Result: {res.status_label} (final set: {final_s})")
    print(f"  Reason: {res.reason}")


def run_overview_demo() -> None:
    samples = [
        ("ATM PIN DFA", validate_pin, ["4821", "0000", "482", "48219", "48a1"]),
        (
            "Password Product DFA",
            validate_password,
            ["Campus@2026", "Ab1!efgh", "campus@2026", "Ab1!efg", "Campus @2026"],
        ),
        (
            "Email Minimal DFA",
            validate_email,
            ["student@srm.edu", "aiml.lab_01@campus-1.edu.in", "student@srm", "stu..dent@srm.edu", "student@srm.c0m"],
        ),
    ]
    for title, fn, inputs in samples:
        print(f"\n--- {title} ---")
        for inp in inputs:
            res = fn(inp)
            print(f"  {inp!r:30s} -> {res.status_label:8s} (final={res.final_state})")

    print_dfa_trace("ATM PIN Trace (Rejected 5-digit)", validate_pin("48219"))
    print_dfa_trace("Password Trace (Accepted)", validate_password("Campus@2026"))
    print_nfa_trace("Email NFA Trace (Branching on '.')", validate_email_nfa("a@b.cd.ef"))
    print_dfa_trace("Email Minimal DFA Trace (Rejected TLD digit)", validate_email("student@srm.c0m"))


def main() -> None:
    if len(sys.argv) == 1:
        run_overview_demo()
        return
    if len(sys.argv) >= 3:
        mode = sys.argv[1].lower()
        val = sys.argv[2]
        if mode == "pin":
            print_dfa_trace("ATM PIN DFA", validate_pin(val))
        elif mode == "password":
            print_dfa_trace("Password Product DFA", validate_password(val))
        elif mode == "email":
            print_nfa_trace("Email NFA", validate_email_nfa(val))
            print_dfa_trace("Email Minimal DFA", validate_email(val))
        else:
            print("Unknown mode. Use: pin | password | email")
            sys.exit(1)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
