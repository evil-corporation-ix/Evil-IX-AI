from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from typing import Optional, Union
import os

DEFAULT_DICTIONARY_PATH = "data/dictionary.txt"


@dataclass(frozen=True)
class SemanticVector:
    time: int
    gender: int
    number: int
    context: int
    polysemy: int

    @classmethod
    def from_string(cls, value: str) -> "SemanticVector":
        parts = value.strip().split(".")
        if len(parts) != 5:
            raise ValueError(f"Invalid 5D vector: {value!r}")
        values = tuple(map(int, parts))
        return cls(*values)

    def to_string(self) -> str:
        return f"{self.time}.{self.gender}.{self.number}.{self.context}.{self.polysemy}"

    def to_dict(self) -> dict:
        return {
            "time": self.time,
            "gender": self.gender,
            "number": self.number,
            "context": self.context,
            "polysemy": self.polysemy,
        }


CONTEXT_TAXONOMY = {
    0: "NONE",
    1: "LOCATION",
    2: "PHYSICAL_OBJECT",
    3: "PERSON",
    4: "ACTIVITY",
    5: "ABSTRACT_CONCEPT",
}


@dataclass(frozen=True)
class DictionaryEntry:
    group_id: int
    word: str
    vector: SemanticVector

    def to_dict(self) -> dict:
        return {
            "group_id": self.group_id,
            "word": self.word,
            "vector": self.vector.to_dict(),
        }


class DictionaryIndex:
    def __init__(self, path: str = DEFAULT_DICTIONARY_PATH):
        self.path = path
        self.entries: list[DictionaryEntry] = []
        self.by_word: dict[str, list[DictionaryEntry]] = defaultdict(list)
        self.by_group: dict[int, list[DictionaryEntry]] = defaultdict(list)
        self.by_context: dict[int, list[DictionaryEntry]] = defaultdict(list)
        self.by_polysemy: dict[int, list[DictionaryEntry]] = defaultdict(list)
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Dictionary not found: {self.path}")

        current_group: Optional[int] = None

        with open(self.path, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                if line.endswith(":") and line[:-1].strip().isdigit():
                    current_group = int(line[:-1].strip())
                    continue

                if current_group is None:
                    raise ValueError(f"Entry without group at line {line_number}")

                if ":" not in line:
                    raise ValueError(f"Invalid dictionary entry at line {line_number}: {line!r}")

                word, vector_text = line.split(":", 1)
                word = word.strip().lower()
                vector_text = vector_text.strip()
                vector = SemanticVector.from_string(vector_text)

                self.add(group_id=current_group, word=word, vector=vector)

    def add(self, group_id: int, word: str, vector: SemanticVector) -> DictionaryEntry:
        entry = DictionaryEntry(
            group_id=group_id,
            word=word.lower(),
            vector=vector,
        )
        self.entries.append(entry)
        self.by_word[entry.word].append(entry)
        self.by_group[entry.group_id].append(entry)
        self.by_context[entry.vector.context].append(entry)
        self.by_polysemy[entry.vector.polysemy].append(entry)
        return entry

    def find_word(self, word: str) -> list[DictionaryEntry]:
        return self.by_word.get(word.lower(), [])

    def find_group(self, group_id: int) -> list[DictionaryEntry]:
        return self.by_group.get(group_id, [])

    def find_context(self, context_id: int) -> list[DictionaryEntry]:
        return self.by_context.get(context_id, [])

    def find_polysemy(self, polysemy_id: int) -> list[DictionaryEntry]:
        return self.by_polysemy.get(polysemy_id, [])

    def stats(self) -> dict:
        return {
            "entries": len(self.entries),
            "words": len(self.by_word),
            "groups": len(self.by_group),
            "contexts": len(self.by_context),
            "polysemy_values": len(self.by_polysemy),
        }


PRIMARY_OPERATORS = {
    "+": "ADD",
    "-": "REMOVE",
    "×": "COMPOSE",
    "÷": "SEPARATE",
    "=": "EQUAL",
    "≈": "APPROXIMATE",
    "≠": "DIFFERENT",
}

DIRECTION_OPERATORS = {
    ">": "FORWARD",
    "<": "REVERSE",
}

STATE_OPERATORS = {
    "!": "ASSERT",
    "?": "UNKNOWN",
}

ALL_OPERATOR_SYMBOLS = (
    set(PRIMARY_OPERATORS)
    | set(DIRECTION_OPERATORS)
    | set(STATE_OPERATORS)
)


@dataclass(frozen=True)
class SemanticOperator:
    symbol: str
    primary: Optional[str] = None
    direction: Optional[str] = None
    state: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "type": "OPERATOR",
            "symbol": self.symbol,
            "primary": self.primary,
            "direction": self.direction,
            "state": self.state,
        }


class OperatorParser:
    @staticmethod
    def parse(expression: str) -> SemanticOperator:
        expression = expression.strip()
        if not expression:
            raise ValueError("Empty operator.")

        primary = None
        direction = None
        state = None

        for symbol in expression:
            if symbol in PRIMARY_OPERATORS:
                if primary is not None:
                    raise ValueError(f"Multiple primary operators: {expression!r}")
                primary = PRIMARY_OPERATORS[symbol]
            elif symbol in DIRECTION_OPERATORS:
                if direction is not None:
                    raise ValueError(f"Multiple direction operators: {expression!r}")
                direction = DIRECTION_OPERATORS[symbol]
            elif symbol in STATE_OPERATORS:
                if state is not None:
                    raise ValueError(f"Multiple state operators: {expression!r}")
                state = STATE_OPERATORS[symbol]
            else:
                raise ValueError(f"Unknown operator symbol: {symbol!r}")

        return SemanticOperator(
            symbol=expression,
            primary=primary,
            direction=direction,
            state=state,
        )


@dataclass(frozen=True)
class SemanticEntity:
    raw_word: str
    normalized_word: str
    entries: tuple[DictionaryEntry, ...]

    def to_dict(self) -> dict:
        return {
            "type": "ENTITY",
            "raw_word": self.raw_word,
            "normalized_word": self.normalized_word,
            "entries": [entry.to_dict() for entry in self.entries],
            "group_ids": [entry.group_id for entry in self.entries],
            "contexts": [
                {
                    "id": entry.vector.context,
                    "name": CONTEXT_TAXONOMY.get(
                        entry.vector.context,
                        "UNKNOWN",
                    ),
                }
                for entry in self.entries
            ],
        }


@dataclass(frozen=True)
class SemanticUnknown:
    raw_value: str

    def to_dict(self) -> dict:
        return {
            "type": "UNKNOWN",
            "raw_value": self.raw_value,
        }


@dataclass(frozen=True)
class SemanticVariant:
    raw_value: str
    variants: tuple

    def to_dict(self) -> dict:
        return {
            "type": "VARIANT",
            "raw_value": self.raw_value,
            "variants": [value.to_dict() for value in self.variants],
        }


@dataclass(frozen=True)
class SemanticReference:
    reference_id: str
    target_group: Optional[int] = None
    target_vector: Optional[str] = None
    source_token: Optional[int] = None
    resolution: str = "EXTERNAL"

    def to_dict(self) -> dict:
        return {
            "type": "REFERENCE",
            "reference_id": self.reference_id,
            "target_group": self.target_group,
            "target_vector": self.target_vector,
            "source_token": self.source_token,
            "resolution": self.resolution,
        }


class ReferenceTable:
    def __init__(self):
        self._references: dict[str, SemanticReference] = {}

    def add(self, reference: SemanticReference) -> None:
        self._references[reference.reference_id] = reference

    def get(self, reference_id: str) -> Optional[SemanticReference]:
        return self._references.get(reference_id)

    def contains(self, reference_id: str) -> bool:
        return reference_id in self._references

    def to_dict(self) -> dict:
        return {
            key: value.to_dict()
            for key, value in self._references.items()
        }


SemanticToken = Union[
    SemanticEntity,
    SemanticOperator,
    SemanticUnknown,
    SemanticVariant,
    SemanticReference,
]


@dataclass(frozen=True)
class TokenPosition:
    index: int
    token_type: str

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "type": self.token_type,
        }


@dataclass(frozen=True)
class ExpressionStructure:
    positions: tuple[TokenPosition, ...]

    def to_dict(self) -> dict:
        return {
            "length": len(self.positions),
            "positions": [position.to_dict() for position in self.positions],
        }


@dataclass(frozen=True)
class SemanticExpression:
    tokens: tuple[SemanticToken, ...]

    def structure(self) -> ExpressionStructure:
        positions = [
            TokenPosition(
                index=index,
                token_type=token.to_dict()["type"],
            )
            for index, token in enumerate(self.tokens)
        ]
        return ExpressionStructure(positions=tuple(positions))

    def to_dict(self) -> dict:
        return {
            "type": "EXPRESSION",
            "tokens": [token.to_dict() for token in self.tokens],
            "structure": self.structure().to_dict(),
        }


class EvilIXCore:
    def __init__(self, dictionary_path: str = DEFAULT_DICTIONARY_PATH):
        self.dictionary = DictionaryIndex(dictionary_path)
        self.references = ReferenceTable()

    def parse_word(self, word: str) -> Union[SemanticEntity, SemanticUnknown]:
        normalized = word.strip().lower()
        entries = self.dictionary.find_word(normalized)

        if not entries:
            return SemanticUnknown(raw_value=word)

        return SemanticEntity(
            raw_word=word,
            normalized_word=normalized,
            entries=tuple(entries),
        )

    def parse_operator(self, expression: str) -> SemanticOperator:
        return OperatorParser.parse(expression)

    def parse_token(self, token: str) -> Optional[SemanticToken]:
        token = token.strip()
        if not token:
            return None

        if all(character in ALL_OPERATOR_SYMBOLS for character in token):
            return self.parse_operator(token)

        if "/" in token:
            parts = tuple(
                part.strip()
                for part in token.split("/")
                if part.strip()
            )
            return SemanticVariant(
                raw_value=token,
                variants=tuple(self.parse_word(part) for part in parts),
            )

        return self.parse_word(token)

    def parse(self, tokens: list[str]) -> SemanticExpression:
        parsed = []
        for token in tokens:
            result = self.parse_token(token)
            if result is not None:
                parsed.append(result)

        return SemanticExpression(tokens=tuple(parsed))

    def lookup(self, word: str) -> list[DictionaryEntry]:
        return self.dictionary.find_word(word)

    def add_reference(self, reference: SemanticReference) -> None:
        self.references.add(reference)

    def get_reference(self, reference_id: str) -> Optional[SemanticReference]:
        return self.references.get(reference_id)

    def parse_to_dict(self, tokens: list[str]) -> dict:
        return self.parse(tokens).to_dict()
