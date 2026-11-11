"""Core Nondeterministic Finite Automaton (NFA) engine and subset construction.

Supports epsilon transitions, step-by-step active-state-set tracing,
and formal powerset (subset) construction converting an NFA into an
equivalent complete DFA.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

from automata.dfa import DFA


EPSILON = "ε"


@dataclass(frozen=True)
class NFATraceStep:
    """Represents a single symbol transition across active NFA state sets."""

    step: int
    active_states: Tuple[str, ...]
    raw_char: str
    symbol: str
    next_states: Tuple[str, ...]
    note: str = ""


@dataclass
class NFAValidationResult:
    """Captures the outcome and state-set trace of an NFA run."""

    accepted: bool
    input_string: str
    final_states: Tuple[str, ...]
    steps: List[NFATraceStep] = field(default_factory=list)
    reason: str = ""
    automaton_name: str = ""

    @property
    def status_label(self) -> str:
        return "ACCEPTED" if self.accepted else "REJECTED"


class NFA:
    """Nondeterministic Finite Automaton (with optional epsilon moves)."""

    def __init__(
        self,
        name: str,
        states: Iterable[str],
        alphabet: Iterable[str],
        transitions: Dict[Tuple[str, str], Iterable[str]],
        initial_state: str,
        final_states: Iterable[str],
        classifier: Optional[Callable[[str], str]] = None,
        state_descriptions: Optional[Dict[str, str]] = None,
        symbol_descriptions: Optional[Dict[str, str]] = None,
    ) -> None:
        self.name = name
        self.states: Set[str] = set(states)
        self.alphabet: Set[str] = set(alphabet)
        self.transitions: Dict[Tuple[str, str], Set[str]] = {
            k: set(v) for k, v in transitions.items()
        }
        self.initial_state: str = initial_state
        self.final_states: Set[str] = set(final_states)
        self.classifier = classifier
        self.state_descriptions = dict(state_descriptions or {})
        self.symbol_descriptions = dict(symbol_descriptions or {})
        self.validate_definition()

    def validate_definition(self) -> None:
        """Verify formal 5-tuple invariants for the NFA."""
        if self.initial_state not in self.states:
            raise ValueError(
                f"Initial state '{self.initial_state}' is not in Q."
            )
        if not self.final_states.issubset(self.states):
            extra = self.final_states - self.states
            raise ValueError(f"Final states {extra} are not in Q.")
        for (src, sym), targets in self.transitions.items():
            if src not in self.states:
                raise ValueError(f"Transition source '{src}' not in Q.")
            if sym != EPSILON and sym not in self.alphabet:
                raise ValueError(f"Transition symbol '{sym}' not in Sigma.")
            if not targets.issubset(self.states):
                extra = targets - self.states
                raise ValueError(f"Transition targets {extra} not in Q.")

    def classify(self, ch: str) -> str:
        """Map a raw character to an alphabet symbol."""
        if self.classifier is not None:
            return self.classifier(ch)
        return ch

    def epsilon_closure(self, states: Iterable[str]) -> Set[str]:
        """Compute the epsilon-closure ECLOSE(S) of a set of states."""
        closure: Set[str] = set(states)
        stack: List[str] = list(closure)
        while stack:
            state = stack.pop()
            for nxt in self.transitions.get((state, EPSILON), set()):
                if nxt not in closure:
                    closure.add(nxt)
                    stack.append(nxt)
        return closure

    def move(self, states: Iterable[str], symbol: str) -> Set[str]:
        """Compute union of delta(q, symbol) over q in states."""
        result: Set[str] = set()
        for state in states:
            result.update(self.transitions.get((state, symbol), set()))
        return result

    def trace(self, input_string: str) -> NFAValidationResult:
        """Process input_string and record active NFA state-set transitions."""
        if not isinstance(input_string, str):
            raise TypeError("Input must be a string.")

        current_set = self.epsilon_closure({self.initial_state})
        steps: List[NFATraceStep] = []

        for idx, ch in enumerate(input_string, start=1):
            sym = self.classify(ch)
            if sym not in self.alphabet:
                next_set: Set[str] = set()
                note = (
                    f"Character {ch!r} (class '{sym}') is outside accepted "
                    f"alphabet; all active paths die."
                )
            else:
                moved = self.move(current_set, sym)
                next_set = self.epsilon_closure(moved)
                if not next_set:
                    note = f"No valid transition on '{sym}' from {sorted(current_set)}."
                elif len(next_set) > 1:
                    note = (
                        f"Nondeterministic branching: active states = "
                        f"{{{', '.join(sorted(next_set))}}}."
                    )
                else:
                    sole = next(iter(next_set))
                    note = self.state_descriptions.get(sole, "")

            steps.append(
                NFATraceStep(
                    step=idx,
                    active_states=tuple(sorted(current_set)),
                    raw_char=ch,
                    symbol=sym,
                    next_states=tuple(sorted(next_set)),
                    note=note,
                )
            )
            current_set = next_set

        accepted = bool(current_set & self.final_states)
        if accepted:
            accepting_hit = sorted(current_set & self.final_states)
            reason = (
                f"Active state set {{{', '.join(sorted(current_set))}}} "
                f"intersects accepting set F at {accepting_hit}."
            )
        elif not current_set:
            reason = "All NFA execution paths terminated in empty set {} (dead)."
        else:
            reason = (
                f"Active state set {{{', '.join(sorted(current_set))}}} "
                f"contains no accepting state in {sorted(self.final_states)}."
            )

        return NFAValidationResult(
            accepted=accepted,
            input_string=input_string,
            final_states=tuple(sorted(current_set)),
            steps=steps,
            reason=reason,
            automaton_name=self.name,
        )

    def accepts(self, input_string: str) -> bool:
        """Return True iff input_string is in L(N)."""
        return self.trace(input_string).accepted

    def to_dfa(
        self,
        name: Optional[str] = None,
        state_prefix: str = "d",
        trap_name: str = "q_trap",
    ) -> DFA:
        """Convert this NFA into an equivalent complete DFA via subset construction."""
        sorted_alpha = sorted(self.alphabet)
        start_subset = frozenset(self.epsilon_closure({self.initial_state}))

        subset_to_name: Dict[frozenset[str], str] = {}
        descriptions: Dict[str, str] = {}
        queue: deque[frozenset[str]] = deque([start_subset])
        visited: Set[frozenset[str]] = {start_subset}

        counter = 0

        def get_name(sub: frozenset[str]) -> str:
            nonlocal counter
            if sub not in subset_to_name:
                if not sub:
                    subset_to_name[sub] = trap_name
                    descriptions[trap_name] = "Empty NFA subset {} (trap state)"
                else:
                    label = f"{state_prefix}{counter}"
                    counter += 1
                    subset_to_name[sub] = label
                    descriptions[label] = (
                        "NFA subset {" + ", ".join(sorted(sub)) + "}"
                    )
            return subset_to_name[sub]

        init_name = get_name(start_subset)
        transitions: Dict[Tuple[str, str], str] = {}
        finals: Set[str] = set()
        has_empty = False

        while queue:
            cur = queue.popleft()
            cur_name = get_name(cur)
            if cur & self.final_states:
                finals.add(cur_name)
            if not cur:
                has_empty = True

            for sym in sorted_alpha:
                nxt = frozenset(self.epsilon_closure(self.move(cur, sym)))
                if not nxt:
                    has_empty = True
                nxt_name = get_name(nxt)
                transitions[(cur_name, sym)] = nxt_name
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        return DFA(
            name=name or f"{self.name} (Subset DFA)",
            states=set(subset_to_name.values()),
            alphabet=self.alphabet,
            transitions=transitions,
            initial_state=init_name,
            final_states=finals,
            trap_state=trap_name if has_empty else None,
            classifier=self.classifier,
            state_descriptions=descriptions,
            symbol_descriptions=self.symbol_descriptions,
        )
