"""Automated unit and independent property tests for ATM PIN Validator DFA."""

import itertools
import re
import unittest

from automata.pin_validator import (
    PIN_DFA,
    check_registered_pin_semantic,
    validate_pin,
)


def independent_pin_spec(s: str) -> bool:
    """Independent reference specification without using the DFA engine."""
    return bool(re.fullmatch(r"[0-9]{4}", s))


class TestATMPinValidator(unittest.TestCase):
    """Test suite for Application 1: ATM PIN Verification DFA."""

    ACCEPTED_CASES = [
        ("4821", "4 valid numeric digits -> q4"),
        ("0000", "4 leading-zero digits -> q4"),
        ("9375", "4 distinct digits -> q4"),
        ("1234", "Sequential 4 digits -> q4"),
        ("0042", "Zero-padded 4 digits -> q4"),
        ("9999", "Maximum 4-digit numeric string -> q4"),
    ]

    REJECTED_CASES = [
        ("", "Empty string stays in initial state q0"),
        ("7", "1 digit ends in q1 (too short)"),
        ("482", "3 digits ends in q3 (boundary below 4)"),
        ("48219", "5 digits transitions q4 -> q_trap (boundary above 4)"),
        ("123456", "6 digits stays in q_trap"),
        ("48a1", "Alphabetic character 'a' outside Sigma -> q_trap"),
        ("12 34", "Space character outside Sigma -> q_trap"),
        ("-123", "Minus sign '-' outside Sigma -> q_trap"),
        ("4,821", "Comma ',' outside Sigma -> q_trap"),
    ]

    def test_formal_dfa_properties(self) -> None:
        self.assertEqual(len(PIN_DFA.states), 6)
        self.assertEqual(PIN_DFA.initial_state, "q0")
        self.assertEqual(PIN_DFA.final_states, {"q4"})
        self.assertEqual(PIN_DFA.trap_state, "q_trap")
        self.assertTrue(PIN_DFA.is_complete())

    def test_accepted_cases(self) -> None:
        for pin, _ in self.ACCEPTED_CASES:
            with self.subTest(pin=pin):
                res = validate_pin(pin)
                self.assertTrue(res.accepted)
                self.assertEqual(res.final_state, "q4")
                self.assertEqual(len(res.steps), 4)

    def test_rejected_cases(self) -> None:
        for pin, _ in self.REJECTED_CASES:
            with self.subTest(pin=pin):
                res = validate_pin(pin)
                self.assertFalse(res.accepted)
                self.assertNotEqual(res.final_state, "q4")

    def test_step_by_step_trace_five_digits(self) -> None:
        res = validate_pin("12345")
        self.assertFalse(res.accepted)
        self.assertEqual(res.final_state, "q_trap")
        states_path = [s.next_state for s in res.steps]
        self.assertEqual(states_path, ["q1", "q2", "q3", "q4", "q_trap"])
        self.assertTrue(res.steps[-1].is_trap)

    def test_step_by_step_trace_invalid_char(self) -> None:
        res = validate_pin("12x4")
        self.assertFalse(res.accepted)
        self.assertEqual(res.final_state, "q_trap")
        self.assertEqual(res.steps[2].symbol, "INVALID(x)")
        self.assertEqual(res.steps[2].next_state, "q_trap")
        self.assertEqual(res.steps[3].next_state, "q_trap")

    def test_independent_exhaustive_verification(self) -> None:
        """Verify DFA against independent regex over all <=4 digit strings + samples."""
        # All 10,000 four-digit PINs must be accepted
        for num in range(10000):
            s = f"{num:04d}"
            self.assertTrue(PIN_DFA.accepts(s))
            self.assertEqual(PIN_DFA.accepts(s), independent_pin_spec(s))

        # Exhaustive strings up to length 5 over {'0', '5', 'a', ' '}
        for length in range(0, 6):
            for tup in itertools.product("05a ", repeat=length):
                s = "".join(tup)
                self.assertEqual(
                    PIN_DFA.accepts(s),
                    independent_pin_spec(s),
                    msg=f"Mismatch on {s!r}",
                )

    def test_syntax_vs_semantic_boundary(self) -> None:
        registered = {"4821", "9375"}
        ok, msg = check_registered_pin_semantic("4821", registered)
        self.assertTrue(ok)
        self.assertIn("matched", msg)

        ok2, msg2 = check_registered_pin_semantic("1234", registered)
        self.assertFalse(ok2)
        self.assertIn("semantic", msg2.lower())

        ok3, msg3 = check_registered_pin_semantic("12ab", registered)
        self.assertFalse(ok3)
        self.assertIn("syntax", msg3.lower())


if __name__ == "__main__":
    unittest.main()
