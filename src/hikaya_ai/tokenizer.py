import json
import re
from pathlib import Path


class HikayaTokenizer:
    def __init__(self):
        self.token_to_id = {
            "<PAD>": 0,
            "<UNK>": 1,
            "<BOS>": 2,
            "<EOS>": 3
        }
        self.id_to_token = {
            value: key
            for key, value in self.token_to_id.items()
        }

    def split_text(self, text):
        return re.findall(
            r"\w+|[^\w\s]",
            text,
            flags=re.UNICODE
        )

    def fit(self, texts):
        for text in texts:
            for token in self.split_text(text):
                if token not in self.token_to_id:
                    token_id = len(self.token_to_id)
                    self.token_to_id[token] = token_id
                    self.id_to_token[token_id] = token

    def encode(self, text):
        tokens = self.split_text(text)
        return [
            self.token_to_id.get(token, 1)
            for token in tokens
        ]

    def decode(self, token_ids):
        tokens = [
            self.id_to_token.get(token_id, "<UNK>")
            for token_id in token_ids
        ]
        return " ".join(tokens)

    def save(self, path):
        Path(path).parent.mkdir(
            parents=True,
            exist_ok=True
        )
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                self.token_to_id,
                file,
                ensure_ascii=False,
                indent=2
            )

    def load(self, path):
        with open(path, "r", encoding="utf-8") as file:
            self.token_to_id = json.load(file)

        self.id_to_token = {
            int(value): key
            for key, value in self.token_to_id.items()
      }
