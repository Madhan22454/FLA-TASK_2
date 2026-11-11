"""Automated unit and independent property tests for Password Validator DFA."""

import random
import unittest

from automata.password_validator import (
    PASSWORD_COMPONENTS,
    PASSWORD_DFA,
    PASSWORD_MINIMAL_DFA,
    SPECIAL_CHARACTERS,
    check_password_authentication_semantic,
    validate_password,
)


def independent_password_spec(s: str) -> bool:
    """Independent procedural specification of the password policy."""
    if not (8 <= len(s) <= 16):
        return False
    has_u = any("A" <= c <= "Z" for c in s)
    has_l = any("a" <= c <= "z" for c in s)
    has_d = any("0" <= c <= "9" for c in s)
    has_s = any(c in SPECIAL_CHARACTERS for c in s)
    all_allowed = all(
        ("A" <= c <= "Z")
        or ("a" <= c <= "z")
        or ("0" <= c <= "9")
        or (c in SPECIAL_CHARACTERS)
        for c in s
    )
    return has_u and has_l and has_d and has_s and all_allowed


class TestPasswordValidator(unittest.TestCase):
    """Test suite for Application 2: Password Strength & Format DFA."""

    ACCEPTED_CASES = [
        ("Ab1!efgh", "Minimum boundary: exactly 8 chars with U, L, D, S"),
        ("Campus@2026", "11 chars with all 4 classes"),
        ("Trichy#99Ai", "11 chars with mixed classes"),
        ("K7$mNp2qR8vW!xZ4", "Maximum boundary: exactly 16 chars with all 4 classes"),
        ("9_ZeroOneA", "10 chars starting with digit and underscore"),
        ("Pass/Word*5", "11 chars with slash and asterisk special characters"),
    ]

    REJECTED_CASES = [
        ("", "Empty string (length 0 < 8)"),
        ("Ab1!efg", "Length 7 (< 8 minimum boundary)"),
        ("Ab1!efghIjklMn0pQ", "Length 17 (> 16 maximum boundary) -> q_trap"),
        ("campus@2026", "Missing uppercase letter U"),
        ("CAMPUS@2026", "Missing lowercase letter L"),
        ("Campus@Aiml", "Missing numeric digit D"),
        ("Campus2026", "Missing special character S"),
        ("Campus @2026", "Contains whitespace (class O) -> q_trap"),
        ("Campus@2026\n", "Contains newline control char (class O) -> q_trap"),
        ("Passw0rd!é", "Contains non-ASCII char 'é' (class O) -> q_trap"),
    ]

    def test_formal_product_and_minimization_properties(self) -> None:
        self.assertTrue(PASSWORD_DFA.is_complete())
        self.assertTrue(PASSWORD_MINIMAL_DFA.is_complete())
        self.assertEqual(len(PASSWORD_COMPONENTS), 5)
        self.assertLessEqual(
            len(PASSWORD_MINIMAL_DFA.states), len(PASSWORD_DFA.states)
        )

    def test_accepted_cases(self) -> None:
        for pwd, _ in self.ACCEPTED_CASES:
            with self.subTest(pwd=pwd):
                res = validate_password(pwd)
                self.assertTrue(res.accepted)
                self.assertTrue(PASSWORD_MINIMAL_DFA.accepts(pwd))
                self.assertTrue(all(d.accepts(pwd) for d in PASSWORD_COMPONENTS))

    def test_rejected_cases(self) -> None:
        for pwd, _ in self.REJECTED_CASES:
            with self.subTest(pwd=pwd):
                res = validate_password(pwd)
                self.assertFalse(res.accepted)
                self.assertFalse(PASSWORD_MINIMAL_DFA.accepts(pwd))
                self.assertFalse(all(d.accepts(pwd) for d in PASSWORD_COMPONENTS))

    def test_trap_state_on_other_char_and_overlength(self) -> None:
        res_space = validate_password("Ab1! efgh")
        self.assertFalse(res_space.accepted)
        self.assertEqual(res_space.final_state, "q_trap")
        self.assertTrue(res_space.steps[4].is_trap)

        res_long = validate_password("Ab1!efghIjklMn0pQ")
        self.assertFalse(res_long.accepted)
        self.assertEqual(res_long.final_state, "q_trap")
        self.assertTrue(res_long.steps[-1].is_trap)

    def test_independent_randomized_equivalence(self) -> None:
        """Compare Product DFA, Minimal DFA, Component DFAs, and Python spec."""
        rng = random.Random(20260301)
        pool = "ABCabc012!@# "
        for _ in range(5000):
            length = rng.randint(0, 19)
            candidate = "".join(rng.choice(pool) for _ in range(length))
            expected = independent_password_spec(candidate)
            self.assertEqual(PASSWORD_DFA.accepts(candidate), expected)
            self.assertEqual(PASSWORD_MINIMAL_DFA.accepts(candidate), expected)
            self.assertEqual(
                all(d.accepts(candidate) for d in PASSWORD_COMPONENTS), expected
            )

    def test_syntax_vs_authentication_boundary(self) -> None:
        vault = {"Campus@2026", "K7$mNp2qR8vW!xZ4"}
        ok, msg = check_password_authentication_semantic("Campus@2026", vault)
        self.assertTrue(ok)
        self.assertIn("matched", msg)

        ok2, msg2 = check_password_authentication_semantic("Other#2026", vault)
        self.assertFalse(ok2)
        self.assertIn("semantic", msg2.lower())

        ok3, msg3 = check_password_authentication_semantic("weak", vault)
        self.assertFalse(ok3)
        self.assertIn("syntax", msg3.lower())


if __name__ == "__main__":
    unittest.main()
