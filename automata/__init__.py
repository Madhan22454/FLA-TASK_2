"""Finite Automata-Based Real-Time Input Validation System."""

from automata.dfa import DFA, TraceStep, ValidationResult, product_dfa
from automata.nfa import EPSILON, NFA, NFATraceStep, NFAValidationResult
from automata.pin_validator import (
    PIN_DFA,
    build_pin_dfa,
    check_registered_pin_semantic,
    validate_pin,
)
from automata.password_validator import (
    PASSWORD_COMPONENTS,
    PASSWORD_DFA,
    PASSWORD_MINIMAL_DFA,
    build_password_components,
    build_password_dfa,
    check_password_authentication_semantic,
    classify_password_char,
    validate_password,
)
from automata.email_validator import (
    EMAIL_DFA,
    EMAIL_NFA,
    EMAIL_SUBSET_DFA,
    build_email_nfa,
    check_email_deliverability_semantic,
    classify_email_char,
    validate_email,
    validate_email_nfa,
)

__all__ = [
    "DFA",
    "NFA",
    "EPSILON",
    "TraceStep",
    "NFATraceStep",
    "ValidationResult",
    "NFAValidationResult",
    "product_dfa",
    "PIN_DFA",
    "build_pin_dfa",
    "validate_pin",
    "check_registered_pin_semantic",
    "PASSWORD_COMPONENTS",
    "PASSWORD_DFA",
    "PASSWORD_MINIMAL_DFA",
    "build_password_components",
    "build_password_dfa",
    "classify_password_char",
    "validate_password",
    "check_password_authentication_semantic",
    "EMAIL_NFA",
    "EMAIL_SUBSET_DFA",
    "EMAIL_DFA",
    "build_email_nfa",
    "classify_email_char",
    "validate_email",
    "validate_email_nfa",
    "check_email_deliverability_semantic",
]
