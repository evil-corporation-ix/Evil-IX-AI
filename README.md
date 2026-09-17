# Evil-IX-AI # AI # symbolic-ai # python
Fully open-source symbolic AI system. Разработка открытого символического искусственного интеллекта.

# Evil.IX.AI Semantic Architecture 

**Evil.IX.AI** is a deterministic, non-LLM semantic parser designed to eliminate AI hallucinations. Instead of relying on probabilistic neural embeddings, it uses a strict vector-based identification system (`ID FORM`) and a logical operator pipeline to process language mathematically.

This repository provides the core MVP (Minimum Viable Product) of the Evil.IX pipeline, featuring positional typo-correction, semantic vectorization, and logical flow parsing.

Core Features

## 1. ID FORM (Context & Association Module)
Words are not stored as strings. They are converted into an absolute 5-dimensional numerical vector (`ID FORM FULL`) that hardcodes their exact semantic and grammatical state.
**Format:** `[Meaning].[Time].[Gender/Number].[Context].[Polysemy]`
* **Example:** `came_m` ➔ `1.1.1.0.0`
  * `1` - Meaning ID (The action of "coming")
  * `1` - Time (Past tense)
  * `1` - Gender/Number (Male / Singular)
  * `0` - Context (Default)
  * `0` - Polysemy (Base meaning)

## 2. Anti-Hallucination Typo Correction
Instead of guessing typos via an LLM, the `LetterLevelParser` uses deterministic positional character overlap. If an input word is misspelled (e.g., `cam_m`), the system calculates its similarity to the dictionary. If the overlap is below the threshold (`< 2`), it is strictly rejected as noise (`STATE[?]`), preventing cascade errors.

## 3. Custom DSL Logic (Operator Pipeline)
The system processes sentences as mathematical equations, converting text into a stack of semantic entities and logical modifiers.

| Symbol | Category | Description |
|---|---|---|
| `+`, `-` | Modifiers | Add or Remove Entities / Context |
| `×`, `÷`, `%` | Scaling | Compose, Decompose, or calculate overlap |
| `=`, `≈`, `≠`, `≡` | Equivalence | Identity Match, Approximation, Contradiction |
| `>`, `<` | Flow | Directed Action Vector, Dependency trace |
| `/` | Transition | Proceed to the next state |
| `!`, `?` | States | Absolute Assertion, or UNKNOWN/Noise state |

---

##Getting Started

##Prerequisites
* Python 3.7 or higher
* No external dependencies (Built with standard Python libraries)

##Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/evil-ix-architecture.git](https://github.com/YOUR_USERNAME/evil-ix-architecture.git)
   cd evil-ix-architecture.

Running the Demo
​Execute the core parser to see how it handles a dirty input stream ("i cam_m + came_f / > x"): python main.py

RAW INPUT STREAM: i cam_m + came_f / > x

PROCESSED EVIL.IX PIPELINE STACK:
 > ENTITY[2.0.0.0.0]
 > ENTITY[1.1.1.0.0]
 > MODIFIER[+]
 > ENTITY[1.1.2.0.0]
 > TRANSITION[Next]
 > COMPARE[>]
 > STATE[?]

Configuration & Customization
​The system relies on external .txt files for definitions, meaning you do not need to edit the Python code to teach the system new words.
​Adding Words to the Dictionary
​Open or create data/dictionary.txt. Add your vocabulary mapping the word to its ID FORM FULL vector.
​Syntax: word:MEANING.TIME.GENDER.CONTEXT.POLYSEMY
​Example data/dictionary.txt:
# Subject / Pronouns
i:2.0.0.0.0
he:2.0.1.0.0
she:2.0.2.0.0

# Actions
run:3.2.0.0.0
ran:3.1.0.0.0

# Polysemy Example (Bank)
bank_river:4.0.0.1.1
bank_money:4.0.0.2.2
Note: Ensure all words are lowercase. The system automatically normalizes inputs.

Expanding Operator Rules
​The data/ folder also contains files for operator logic (plus_minus.txt, equality.txt, etc.). While the current Python script parses the operators, you can use these .txt files in the future to map specific mathematical functions or execution behaviors to these symbols.
​##Project Structure
evil-ix-architecture/
│
├── main.py              # The core engine (Parser, IDForm, TypoCorrection)
├── README.md            # Documentation
└── data/                # Logic and vocabulary storage
    ├── dictionary.txt       # The Main ID FORM definitions
    ├── plus_minus.txt       # Rules for +/-
    ├── equality.txt         # Rules for =/≈/≠/≡
    └── ... 




