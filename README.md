# Finite Automata-Based Real-Time Input Validation System

**Course:** `21CSC301T – Formal Language and Automata`  
**Assessment:** Continuous Learning Assessment 2 (CLA-2) – Task 2  
**Institution:** Department of Artificial Intelligence and Machine Learning, SRM Institute of Science and Technology, Tiruchirappalli  
**Faculty:** Dr. C. Gunasundari (Assistant Professor)  
**Academic Year:** 2026–2027 (Semester V)  
**SDG Alignment:** SDG 9 – Industry, Innovation and Infrastructure (Level 2: Design Alignment)

---

## Project Overview

This repository implements a complete **Finite Automata-Based Real-Time Input Validation System** in Python with an interactive **Streamlit** web interface and formal **automata diagram generator**. The system models syntactic input validation across three practical engineering domains using Deterministic Finite Automata (DFA), Nondeterministic Finite Automata (NFA), Cartesian product construction, subset (powerset) construction, and partition-refinement minimization:

1. **ATM PIN Verification System** — Complete 6-state DFA over $\Sigma = \{0, 1, \dots, 9\}$ accepting $L_{\mathrm{PIN}} = \{w \in \Sigma^* : |w| = 4\}$, with explicit trap state $q_{\mathrm{trap}}$ for length $> 4$ or non-numeric characters.
2. **Password Strength & Format Validator** — Modular intersection of 5 component DFAs ($L_{\mathrm{len}} \cap L_U \cap L_L \cap L_D \cap L_S$) over $\Sigma = \{U, L, D, S, O\}$, combined via formal Cartesian product construction into a 225-state complete DFA (197 states after minimization).
3. **Email Format Validation System** — 9-state NFA ($n_0 \dots n_8$) capturing dot-lookahead nondeterminism in domain labels, converted automatically via subset construction into a 10-state DFA and minimized to an 8-state Minimal DFA ($m_0 \dots m_6, q_{\mathrm{trap}}$).

---

## Objectives

- Formalize real-time validation rules as regular languages with explicit alphabets, state sets, initial states, final states, and transition functions.
- Build reusable, cleanly commented Python `DFA` and `NFA` engines supporting character-by-character transition tracing and invalid-input handling.
- Demonstrate theoretical constructions in code: **NFA $\to$ DFA subset construction**, **DFA Cartesian product construction**, and **DFA partition-refinement minimization**.
- Distinguish **syntactic validation** (regular-language membership checked by an FA) from **semantic/business verification** (bank PIN database lookup, credential authentication, DNS/SMTP mailbox existence).
- Verify correctness through curated accepted/rejected test cases and exhaustive/randomized independent specification testing.

---

## Automata Concepts Used

| Concept | Application in Project |
|---|---|
| **Deterministic Finite Automaton (DFA)** | 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$ implemented in `automata/dfa.py` with completeness validation and trap-state routing. |
| **Nondeterministic Finite Automaton (NFA)** | 5-tuple $N = (Q, \Sigma, \delta, q_0, F)$ implemented in `automata/nfa.py` with $\varepsilon$-closure and active state-set tracing. |
| **Subset (Powerset) Construction** | Automatically converts `EMAIL_NFA` (9 states) into an equivalent complete 10-state DFA (`EMAIL_SUBSET_DFA`). |
| **Product Construction (Closure under $\cap$)** | Combines 5 modular password-policy DFAs into a unified 225-state Product DFA (`PASSWORD_DFA`). |
| **DFA Minimization (Partition Refinement)** | Reduces `PASSWORD_DFA` from 225 to 197 states and `EMAIL_SUBSET_DFA` from 10 to 8 states (`EMAIL_DFA`). |
| **Trap / Sink States** | Explicitly absorbs invalid characters ($\notin \Sigma$), disallowed class `O`, or policy violations deterministically. |

---

## Technologies Used

- **Language:** Python 3.10+ (tested on Python 3.14.6)
- **Interactive Web UI:** Streamlit (`app.py`)
- **Diagram Generation:** Matplotlib (`generate_diagrams.py`)
- **Automated Testing:** `pytest` and `unittest` (`tests/`)
- **Data Formatting & Reporting:** `pandas`, `python-docx`, `Pillow`

---

## Installation

1. Clone the repository:
   ```bash
   git clone <YOUR_GITHUB_REPOSITORY_URL>
   cd FLA-CLA2-TASK2
   ```
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Execution Instructions

### 1. Run the Interactive Streamlit Web Application
```bash
python -m streamlit run app.py
```
Open the local URL printed in the terminal (typically `http://localhost:8501`) to access:
- Project Dashboard & Formal Comparison
- Live ATM PIN Validator (with real-time SVG state highlighting)
- Live Password Strength & Format Validator (with 5 component DFA status cards)
- Live Email Format Validator (toggle between Minimal 8-state DFA and 9-state NFA active-set trace)
- Automated Sample Test Cases Verification

### 2. Run the Command-Line Demonstration
```bash
python cli_demo.py
python cli_demo.py pin 48219
python cli_demo.py password "Campus@2026"
python cli_demo.py email "aiml.lab_01@campus-1.edu.in"
```

### 3. Regenerate Automata Diagrams
```bash
python generate_diagrams.py
```

---

## Test Execution

Run the full automated unit and independent property test suite:
```bash
python -m pytest -v
```
Or using standard-library `unittest`:
```bash
python -m unittest discover -s tests -v
```
The test suite verifies:
- Curated accepted and rejected cases (including boundary lengths, empty strings $\varepsilon$, and invalid characters).
- Exhaustive equivalence of `PIN_DFA` across all 10,000 four-digit PINs and generated strings.
- Equivalence of `PASSWORD_DFA`, `PASSWORD_MINIMAL_DFA`, the 5 `PASSWORD_COMPONENTS`, and an independent Python specification across 5,000 randomized strings.
- Exhaustive equivalence of `EMAIL_NFA`, `EMAIL_SUBSET_DFA`, `EMAIL_DFA`, and an independent regular expression across all 335,923 strings up to length 7 over `{a, 1, ., -, _, @}`.

---

## Screenshots

- **Project Dashboard:** `screenshots/01_dashboard.png`
- **ATM PIN Validator (Accepted & Rejected):** `screenshots/02_pin_accepted.png`, `screenshots/03_pin_rejected.png`
- **Password Validator:** `screenshots/04_password_accepted.png`
- **Email Validator (DFA & NFA):** `screenshots/05_email_accepted.png`, `screenshots/06_email_nfa_rejected.png`
- **Test Cases Matrix & CLI/Pytest Output:** `screenshots/07_test_cases.png`, `screenshots/08_pytest_and_cli.png`

---

## Repository Contents

```text
FLA-CLA2-TASK2/
│
├── app.py                        # Streamlit interactive web interface
├── cli_demo.py                   # Command-line demonstration & trace tool
├── generate_diagrams.py          # Formal automata diagram generator (300 DPI PNG)
├── requirements.txt              # Python package dependencies
├── README.md                     # Project documentation
├── .gitignore                    # Git ignore rules
│
├── automata/
│   ├── __init__.py               # Package exports
│   ├── dfa.py                    # Core DFA engine, product construction, minimization
│   ├── nfa.py                    # Core NFA engine, epsilon-closure, subset construction
│   ├── pin_validator.py          # Application 1: ATM PIN DFA
│   ├── password_validator.py     # Application 2: Password Product DFA
│   └── email_validator.py        # Application 3: Email NFA & Minimal DFA
│
├── tests/
│   ├── test_pin.py               # Unit & exhaustive tests for ATM PIN DFA
│   ├── test_password.py          # Unit & randomized tests for Password DFA
│   └── test_email.py             # Unit & exhaustive tests for Email NFA/DFA
│
├── diagrams/
│   ├── pin_dfa.png               # ATM PIN 6-state DFA diagram + table
│   ├── password_dfa.png          # Password Component + Product DFA diagram
│   └── email_automaton.png       # Email 9-state NFA & Minimal 8-state DFA diagram
│
├── screenshots/                  # Genuine UI & terminal execution screenshots
│
└── report/
    └── CLA2_Task2_Report.docx    # Complete editable academic report
```
