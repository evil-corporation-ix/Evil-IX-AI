import os

PATHS = {
    'dictionary': 'data/dictionary.txt',
    'plus_minus': 'data/plus_minus.txt',
    'multiply_divide': 'data/multiply_divide.txt',
    'property_unknown': 'data/property_unknown.txt',
    'equality': 'data/equality.txt',
    'approximation': 'data/approximation.txt',
    'contradiction': 'data/contradiction.txt',
    'homonymy': 'data/homonymy.txt',
    'less_greater': 'data/less_greater.txt',
    'transition': 'data/transition.txt',
}


class IDForm:
    def __init__(self, meaning_id: int, time: int, gender_number: int, context_class: int, polysemy: int):
        self.meaning_id = meaning_id
        self.time = time
        self.gender_number = gender_number
        self.context_class = context_class
        self.polysemy = polysemy

    @classmethod
    def from_string(cls, id_str: str):
        if id_str == "?":
            return None
        return cls(*map(int, id_str.split('.')))

    def to_full_string(self) -> str:
        return f"{self.meaning_id}.{self.time}.{self.gender_number}.{self.context_class}.{self.polysemy}"

    def to_short_string(self) -> str:
        return f"{self.meaning_id}.{self.time}"


class LetterLevelParser:
    def __init__(self, dict_path: str):
        self.dict_path = dict_path
        self.vocab = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.dict_path):
            self.vocab = {
                "came_m": "1.1.1.0.0",
                "came_f": "1.1.2.0.0",
                "came_p": "1.1.3.0.0",
                "i": "2.0.0.0.0"
            }
            return

        with open(self.dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    word, id_form = line.split(':', 1)
                    self.vocab[word.strip().lower()] = id_form.strip()

    def _similarity(self, s1: str, s2: str) -> int:
        return sum(1 for a, b in zip(s1.lower(), s2.lower()) if a == b)

    def normalize(self, token: str) -> str:
        best_match = None
        max_score = -1

        for dict_word in self.vocab.keys():
            score = self._similarity(token, dict_word)
            if score > max_score:
                max_score = score
                best_match = dict_word

        return best_match if max_score >= 2 else "?"

    def get_id(self, word: str) -> str:
        if word == "?":
            return "?"
        return self.vocab.get(word, "?")


class EvilIXCoreParser:
    def __init__(self, parser: LetterLevelParser):
        self.parser = parser

    def parse(self, expression: str):
        tokens = expression.split()
        res = []
        
        for t in tokens:
            if t in {'+', '-'}:
                res.append(f"MODIFIER[{t}]")
            elif t in {'×', '÷', '%'}:
                res.append(f"SCALE[{t}]")
            elif t in {'=', '≈', '≠', '≡'}:
                res.append(f"EQUIVALENCE[{t}]")
            elif t in {'<', '>'}:
                res.append(f"COMPARE[{t}]")
            elif t == '/':
                res.append("TRANSITION[Next]")
            elif t in {'!', '?'}:
                res.append(f"STATE[{t}]")
            else:
                norm = self.parser.normalize(t)
                vid = self.parser.get_id(norm)
                res.append(f"STATE[?]" if vid == "?" else f"ENTITY[{vid}]")

        return res


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    checker = LetterLevelParser(PATHS['dictionary'])
    core = EvilIXCoreParser(checker)
    
    raw_input = "i cam_m + came_f / > x"
    print("IN:", raw_input)
    for step in core.parse(raw_input):
        print(" >", step)
