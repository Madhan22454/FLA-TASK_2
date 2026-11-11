"""Automated unit and independent property tests for Email Format Automaton."""

import itertools
import re
import unittest

from automata.email_validator import (
    EMAIL_DFA,
    EMAIL_NFA,
    EMAIL_SUBSET_DFA,
    check_email_deliverability_semantic,
    validate_email,
    validate_email_nfa,
)


INDEPENDENT_EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9]+([._-][A-Za-z0-9]+)*@"
    r"[A-Za-z0-9]+(-[A-Za-z0-9]+)*(\.[A-Za-z0-9]+(-[A-Za-z0-9]+)*)*"
    r"\.[A-Za-z]{2,}$"
)


def independent_email_spec(s: str) -> bool:
    """Independent regex reference for our practical email syntax subset."""
    return bool(INDEPENDENT_EMAIL_REGEX.fullmatch(s))


class TestEmailValidator(unittest.TestCase):
    """Test suite for Application 3: Email Format NFA & Minimal DFA."""

    ACCEPTED_CASES = [
        ("student@srm.edu", "Standard local@domain.tld format"),
        ("aiml.lab_01@campus-1.edu.in", "Multi-separator local + subdomain + 2-letter TLD"),
        ("a@b.io", "Minimal valid length (1-char local, 1-char domain label, 2-letter TLD)"),
        ("dept-chair@faculty.university.org", "Hyphen in local and multi-level domain"),
        ("user_99@node2.cloud.info", "Underscore in local part, digit in domain label"),
        ("r2d2@galaxy.tech", "Alphanumeric local and 4-letter TLD"),
    ]

    REJECTED_CASES = [
        ("", "Empty string"),
        ("student", "Missing '@' and domain"),
        ("student@srm", "Missing domain separator dot and TLD"),
        (".student@srm.edu", "Leading dot in local part"),
        ("student.@srm.edu", "Trailing dot in local part before '@'"),
        ("stu..dent@srm.edu", "Consecutive dots in local part"),
        ("student@@srm.edu", "Multiple '@' symbols"),
        ("student@.srm.edu", "Dot immediately after '@'"),
        ("student@srm..edu", "Consecutive dots in domain"),
        ("student@-srm.edu", "Leading hyphen in domain label"),
        ("student@srm-.edu", "Trailing hyphen in domain label"),
        ("student@srm_lab.edu", "Underscore '_' disallowed in domain label"),
        ("student@srm.e", "TLD shorter than 2 letters"),
        ("student@srm.c0m", "Digit inside TLD"),
        ("student@srm.edu.", "Trailing dot after TLD"),
        ("stu dent@srm.edu", "Whitespace character (class OTHER)"),
    ]

    def test_formal_nfa_and_dfa_properties(self) -> None:
        self.assertEqual(len(EMAIL_NFA.states), 9)
        self.assertEqual(len(EMAIL_SUBSET_DFA.states), 10)
        self.assertEqual(len(EMAIL_DFA.states), 8)
        self.assertTrue(EMAIL_SUBSET_DFA.is_complete())
        self.assertTrue(EMAIL_DFA.is_complete())
        self.assertEqual(EMAIL_DFA.trap_state, "q_trap")

    def test_accepted_cases(self) -> None:
        for email, _ in self.ACCEPTED_CASES:
            with self.subTest(email=email):
                dfa_res = validate_email(email)
                nfa_res = validate_email_nfa(email)
                self.assertTrue(dfa_res.accepted)
                self.assertTrue(nfa_res.accepted)
                self.assertTrue(EMAIL_SUBSET_DFA.accepts(email))
                self.assertTrue(independent_email_spec(email))

    def test_rejected_cases(self) -> None:
        for email, _ in self.REJECTED_CASES:
            with self.subTest(email=email):
                dfa_res = validate_email(email)
                nfa_res = validate_email_nfa(email)
                self.assertFalse(dfa_res.accepted)
                self.assertFalse(nfa_res.accepted)
                self.assertFalse(EMAIL_SUBSET_DFA.accepts(email))
                self.assertFalse(independent_email_spec(email))

    def test_nondeterministic_branching_in_nfa_trace(self) -> None:
        """Verify NFA branches into {n3, n6} upon reading '.' in domain."""
        nfa_res = validate_email_nfa("a@b.cd.ef")
        self.assertTrue(nfa_res.accepted)
        dot_steps = [s for s in nfa_res.steps if s.symbol == "DOT"]
        self.assertEqual(len(dot_steps), 2)
        self.assertEqual(dot_steps[0].next_states, ("n3", "n6"))
        self.assertEqual(dot_steps[1].next_states, ("n3", "n6"))
        self.assertIn("n8", nfa_res.final_states)

    def test_independent_exhaustive_equivalence(self) -> None:
        """Test all strings up to length 7 over representative alphabet {a, 1, ., -, _, @}."""
        chars = ("a", "1", ".", "-", "_", "@")
        for length in range(0, 8):
            for tup in itertools.product(chars, repeat=length):
                s = "".join(tup)
                expected = independent_email_spec(s)
                self.assertEqual(EMAIL_NFA.accepts(s), expected, msg=f"NFA mismatch: {s!r}")
                self.assertEqual(EMAIL_SUBSET_DFA.accepts(s), expected, msg=f"Subset DFA mismatch: {s!r}")
                self.assertEqual(EMAIL_DFA.accepts(s), expected, msg=f"Minimal DFA mismatch: {s!r}")

    def test_syntax_vs_mailbox_existence_boundary(self) -> None:
        directory = {"student@srm.edu", "aiml.lab_01@campus-1.edu.in"}
        ok, msg = check_email_deliverability_semantic("student@srm.edu", directory)
        self.assertTrue(ok)
        self.assertIn("exists", msg)

        ok2, msg2 = check_email_deliverability_semantic("nobody@srm.edu", directory)
        self.assertFalse(ok2)
        self.assertIn("no active mailbox", msg2.lower())

        ok3, msg3 = check_email_deliverability_semantic("bad@@srm.edu", directory)
        self.assertFalse(ok3)
        self.assertIn("syntax", msg3.lower())


if __name__ == "__main__":
    unittest.main()
