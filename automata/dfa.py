"""Core Deterministic Finite Automaton (DFA) engine and formal operations.

Provides a mathematically complete 5-tuple DFA model M = (Q, Sigma, delta, q0, F)
with character-by-character transition tracing, invalid-symbol handling,
reachability pruning, product construction (intersection/union), and
partition-refinement minimization.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple


@dataclass(frozen=True)
class TraceStep:
    """Represents a single character transition in an automaton run."""

    step: int
    current_state: str
    raw_char: str
    symbol: str
    next_state: str
    is_trap: bool = False
    note: str = ""


@dataclass
class ValidationResult:
    """Captures the complete outcome and transition trace of an input run."""

    accepted: bool
    input_string: str
    final_state: str
    steps: List[TraceStep] = field(default_factory=list)
    reason: str = ""
    automaton_name: str = ""

    @property
    def status_label(self) -> str:
        return "ACCEPTED" if self.accepted else "REJECTED"


class DFA:
    """Deterministic Finite Automaton M = (Q, Sigma, delta, q0, F)."""

    def __init__(
        self,
        name: str,
        states: Iterable[str],
        alphabet: Iterable[str],
        transitions: Dict[Tuple[str, str], str],
        initial_state: str,
        final_states: Iterable[str],
        trap_state: Optional[str] = None,
        classifier: Optional[Callable[[str], str]] = None,
        state_descriptions: Optional[Dict[str, str]] = None,
        symbol_descriptions: Optional[Dict[str, str]] = None,
    ) -> None:
        self.name = name
        self.states: Set[str] = set(states)
        self.alphabet: Set[str] = set(alphabet)
        self.transitions: Dict[Tuple[str, str], str] = dict(transitions)
        self.initial_state: str = initial_state
        self.final_states: Set[str] = set(final_states)
        self.trap_state: Optional[str] = trap_state
        self.classifier = classifier
        self.state_descriptions = dict(state_descriptions or {})
        self.symbol_descriptions = dict(symbol_descriptions or {})
        self.validate_definition()

    def validate_definition(self) -> None:
        """Verify formal 5-tuple invariants for the DFA."""
        if self.initial_state not in self.states:
            raise ValueError(
                f"Initial state '{self.initial_state}' is not in Q."
            )
        if not self.final_states.issubset(self.states):
            extra = self.final_states - self.states
            raise ValueError(f"Final states {extra} are not in Q.")
        if self.trap_state is not None and self.trap_state not in self.states:
            raise ValueError(
                f"Trap state '{self.trap_state}' is not in Q."
            )
        for (src, sym), dst in self.transitions.items():
            if src not in self.states:
                raise ValueError(f"Transition source '{src}' not in Q.")
            if sym not in self.alphabet:
                raise ValueError(f"Transition symbol '{sym}' not in Sigma.")
            if dst not in self.states:
                raise ValueError(f"Transition target '{dst}' not in Q.")

    def is_complete(self) -> bool:
        """Return True iff delta(q, a) is defined for all q in Q, a in Sigma."""
        return all(
            (q, a) in self.transitions
            for q in self.states
            for a in self.alphabet
        )

    def classify(self, ch: str) -> str:
        """Map a raw input character to an alphabet symbol."""
        if self.classifier is not None:
            return self.classifier(ch)
        return ch

    def step(self, state: str, symbol: str) -> str:
        """Execute a single transition delta(state, symbol)."""
        if (state, symbol) in self.transitions:
            return self.transitions[(state, symbol)]
        if self.trap_state is not None:
            return self.trap_state
        raise KeyError(
            f"No transition defined for state='{state}', symbol='{symbol}'."
        )

    def trace(self, input_string: str) -> ValidationResult:
        """Process input_string character by character and record full trace."""
        if not isinstance(input_string, str):
            raise TypeError("Input must be a string.")

        current = self.initial_state
        steps: List[TraceStep] = []

        for idx, ch in enumerate(input_string, start=1):
            sym = self.classify(ch)
            if sym not in self.alphabet:
                if self.trap_state is not None:
                    nxt = self.trap_state
                    note = (
                        f"Character {ch!r} (class '{sym}') is outside "
                        f"accepted alphabet; routed to trap state {nxt}."
                    )
                    steps.append(
                        TraceStep(
                            step=idx,
                            current_state=current,
                            raw_char=ch,
                            symbol=f"INVALID({sym})",
                            next_state=nxt,
                            is_trap=True,
                            note=note,
                        )
                    )
                    current = nxt
                    continue
                raise ValueError(
                    f"Symbol {sym!r} from char {ch!r} is not in Sigma."
                )

            nxt = self.step(current, sym)
            is_trap = self.trap_state is not None and nxt == self.trap_state
            note = self.state_descriptions.get(nxt, "")
            steps.append(
                TraceStep(
                    step=idx,
                    current_state=current,
                    raw_char=ch,
                    symbol=sym,
                    next_state=nxt,
                    is_trap=is_trap,
                    note=note,
                )
            )
            current = nxt

        accepted = current in self.final_states
        if accepted:
            reason = (
                f"Ended in accepting state '{current}' after reading "
                f"{len(input_string)} character(s)."
            )
        elif self.trap_state is not None and current == self.trap_state:
            reason = (
                f"Ended in trap state '{current}' (rejecting sink state)."
            )
        else:
            reason = (
                f"Ended in non-accepting state '{current}' "
                f"(final states: {sorted(self.final_states)})."
            )

        return ValidationResult(
            accepted=accepted,
            input_string=input_string,
            final_state=current,
            steps=steps,
            reason=reason,
            automaton_name=self.name,
        )

    def accepts(self, input_string: str) -> bool:
        """Return True iff input_string is in L(M)."""
        return self.trace(input_string).accepted

    def reachable_states(self) -> Set[str]:
        """Compute all states reachable from initial_state via BFS."""
        visited: Set[str] = {self.initial_state}
        queue: deque[str] = deque([self.initial_state])
        while queue:
            state = queue.popleft()
            for sym in sorted(self.alphabet):
                if (state, sym) in self.transitions:
                    nxt = self.transitions[(state, sym)]
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)
        return visited

    def reachable_dfa(self) -> "DFA":
        """Return an equivalent DFA restricted to reachable states."""
        reach = self.reachable_states()
        transitions = {
            (s, a): t
            for (s, a), t in self.transitions.items()
            if s in reach and t in reach
        }
        trap = self.trap_state if self.trap_state in reach else None
        return DFA(
            name=f"{self.name} (Reachable)",
            states=reach,
            alphabet=self.alphabet,
            transitions=transitions,
            initial_state=self.initial_state,
            final_states=self.final_states & reach,
            trap_state=trap,
            classifier=self.classifier,
            state_descriptions={
                k: v for k, v in self.state_descriptions.items() if k in reach
            },
            symbol_descriptions=self.symbol_descriptions,
        )

    def minimize(self, state_prefix: str = "m") -> "DFA":
        """Minimize a complete DFA via Moore/Hopcroft partition refinement."""
        base = self.reachable_dfa()
        if not base.is_complete():
            raise ValueError("DFA must be complete before minimization.")

        accepting = frozenset(base.final_states)
        non_accepting = frozenset(base.states - base.final_states)
        partitions: List[frozenset[str]] = [
            part for part in (accepting, non_accepting) if part
        ]

        sorted_alphabet = sorted(base.alphabet)
        changed = True
        while changed:
            changed = False
            state_to_block = {
                s: idx
                for idx, block in enumerate(partitions)
                for s in block
            }
            new_partitions: List[frozenset[str]] = []
            for block in partitions:
                if len(block) <= 1:
                    new_partitions.append(block)
                    continue
                groups: Dict[Tuple[int, ...], List[str]] = {}
                for s in sorted(block):
                    sig = tuple(
                        state_to_block[base.transitions[(s, a)]]
                        for a in sorted_alphabet
                    )
                    groups.setdefault(sig, []).append(s)
                if len(groups) > 1:
                    changed = True
                for members in groups.values():
                    new_partitions.append(frozenset(members))
            partitions = new_partitions

        # Order blocks deterministically: initial state first, trap state last.
        def sort_key(block: frozenset[str]) -> Tuple[int, str]:
            if base.initial_state in block:
                return (0, base.initial_state)
            if base.trap_state is not None and base.trap_state in block:
                return (2, base.trap_state)
            return (1, min(block))

        partitions.sort(key=sort_key)

        block_names: Dict[frozenset[str], str] = {}
        state_to_name: Dict[str, str] = {}
        descriptions: Dict[str, str] = {}
        counter = 0
        for block in partitions:
            if base.trap_state is not None and base.trap_state in block:
                # Check if block is truly a non-accepting sink trap
                is_sink = (
                    not (block & base.final_states)
                    and all(
                        base.transitions[(next(iter(block)), a)] in block
                        for a in sorted_alphabet
                    )
                )
                label = "q_trap" if is_sink else f"{state_prefix}{counter}"
                if not is_sink:
                    counter += 1
            else:
                label = f"{state_prefix}{counter}"
                counter += 1
            block_names[block] = label
            for s in block:
                state_to_name[s] = label
            descriptions[label] = "Merged states: {" + ", ".join(sorted(block)) + "}"

        min_states = set(block_names.values())
        min_initial = state_to_name[base.initial_state]
        min_finals = {state_to_name[s] for s in base.final_states}
        min_transitions: Dict[Tuple[str, str], str] = {}
        for block in partitions:
            rep = next(iter(block))
            src_name = block_names[block]
            for a in sorted_alphabet:
                dst_name = state_to_name[base.transitions[(rep, a)]]
                min_transitions[(src_name, a)] = dst_name

        min_trap = "q_trap" if "q_trap" in min_states else None

        return DFA(
            name=f"{self.name} (Minimal)",
            states=min_states,
            alphabet=base.alphabet,
            transitions=min_transitions,
            initial_state=min_initial,
            final_states=min_finals,
            trap_state=min_trap,
            classifier=self.classifier,
            state_descriptions=descriptions,
            symbol_descriptions=self.symbol_descriptions,
        )

    def transition_table_rows(
        self, ordered_states: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """Return transition table rows suitable for UI tables and reports."""
        states = ordered_states or sorted(self.states)
        symbols = sorted(self.alphabet)
        rows: List[Dict[str, str]] = []
        for s in states:
            prefix = ""
            if s == self.initial_state and s in self.final_states:
                prefix = "->* "
            elif s == self.initial_state:
                prefix = "-> "
            elif s in self.final_states:
                prefix = "* "
            row: Dict[str, str] = {"State": f"{prefix}{s}"}
            for sym in symbols:
                row[sym] = self.transitions.get((s, sym), "-")
            rows.append(row)
        return rows


def product_dfa(
    dfas: List[DFA],
    name: str,
    mode: str = "intersection",
    trap_name: str = "q_trap",
    classifier: Optional[Callable[[str], str]] = None,
) -> DFA:
    """Construct the reachable product DFA over a shared alphabet.

    Args:
        dfas: Non-empty list of DFAs sharing identical alphabets.
        name: Name for the resulting product DFA.
        mode: 'intersection' (accept iff all DFAs accept) or 'union'
            (accept iff at least one DFA accepts).
        trap_name: Canonical sink state name when any component hits a sink
            trap state in intersection mode.
        classifier: Optional shared character classifier.
    """
    if not dfas:
        raise ValueError("At least one DFA is required for product_dfa.")
    if mode not in {"intersection", "union"}:
        raise ValueError("mode must be 'intersection' or 'union'.")

    alphabet = set(dfas[0].alphabet)
    for dfa in dfas[1:]:
        if set(dfa.alphabet) != alphabet:
            raise ValueError("All DFAs in product construction must share Sigma.")

    sorted_alpha = sorted(alphabet)

    def is_component_sink_trap(dfa: DFA, state: str) -> bool:
        if dfa.trap_state != state or state in dfa.final_states:
            return False
        return all(dfa.transitions.get((state, a)) == state for a in sorted_alpha)

    def tuple_to_name(tup: Tuple[str, ...]) -> str:
        if mode == "intersection" and any(
            is_component_sink_trap(d, s) for d, s in zip(dfas, tup)
        ):
            return trap_name
        return "(" + ",".join(tup) + ")"

    init_tup = tuple(d.initial_state for d in dfas)
    init_name = tuple_to_name(init_tup)

    states: Set[str] = {init_name}
    finals: Set[str] = set()
    transitions: Dict[Tuple[str, str], str] = {}
    descriptions: Dict[str, str] = {}

    visited_tuples: Set[Tuple[str, ...]] = {init_tup}
    queue: deque[Tuple[str, ...]] = deque([init_tup])

    has_trap = False
    while queue:
        cur_tup = queue.popleft()
        cur_name = tuple_to_name(cur_tup)

        if cur_name == trap_name:
            has_trap = True
            for sym in sorted_alpha:
                transitions[(trap_name, sym)] = trap_name
            descriptions[trap_name] = "Sink trap state (policy violated)"
            continue

        if mode == "intersection":
            if all(s in d.final_states for d, s in zip(dfas, cur_tup)):
                finals.add(cur_name)
        else:
            if any(s in d.final_states for d, s in zip(dfas, cur_tup)):
                finals.add(cur_name)

        descriptions[cur_name] = "Product state " + cur_name

        for sym in sorted_alpha:
            nxt_tup = tuple(
                d.step(s, sym) for d, s in zip(dfas, cur_tup)
            )
            nxt_name = tuple_to_name(nxt_tup)
            transitions[(cur_name, sym)] = nxt_name
            states.add(nxt_name)
            if nxt_name == trap_name:
                has_trap = True
                for a in sorted_alpha:
                    transitions[(trap_name, a)] = trap_name
                descriptions[trap_name] = "Sink trap state (policy violated)"
            elif nxt_tup not in visited_tuples:
                visited_tuples.add(nxt_tup)
                queue.append(nxt_tup)

    return DFA(
        name=name,
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state=init_name,
        final_states=finals,
        trap_state=trap_name if has_trap else None,
        classifier=classifier or dfas[0].classifier,
        state_descriptions=descriptions,
        symbol_descriptions=dfas[0].symbol_descriptions,
    )
