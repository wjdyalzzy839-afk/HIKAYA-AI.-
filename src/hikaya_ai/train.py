from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from .model import HikayaAI, HikayaConfig
from .tokenizer import HikayaTokenizer


ROOT = Path(__file__).resolve().parents[2]


class HikayaDataset(Dataset):
    def __init__(self, texts, tokenizer, seq_len=64):
        self.samples = []

        for text in texts:
            ids = tokenizer.encode(text)

            for start in range(0, len(ids) - 1, seq_len):
                chunk = ids[start:start + seq_len + 1]

                if len(chunk) >= 2:
                    chunk += [0] * (seq_len + 1 - len(chunk))
                    self.samples.append(chunk)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        chunk = self.samples[index]

        return (
            torch.tensor(chunk[:-1], dtype=torch.long),
            torch.tensor(chunk[1:], dtype=torch.long)
        )


def train_model(epochs=10, batch_size=4):
    data_path = ROOT / "data" / "training.txt"

    if not data_path.exists():
        raise FileNotFoundError("ملف بيانات التدريب غير موجود.")

    texts = [
        line.strip()
        for line in data_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    tokenizer = HikayaTokenizer()
    tokenizer.fit(texts)

    config = type(
        "Config",
        (HikayaConfig,),
        {"vocab_size": max(4, len(tokenizer.token_to_id))}
    )

    dataset = HikayaDataset(texts, tokenizer)

    if len(dataset) == 0:
        raise ValueError("بيانات التدريب غير كافية.")

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True
    )

    model = HikayaAI(config)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=0.0003
    )

    criterion = nn.CrossEntropyLoss(ignore_index=0)
    model.train()

    for epoch in range(epochs):
        total_loss = 0

        for inputs, targets in loader:
            optimizer.zero_grad()

            outputs = model(inputs)

            loss = criterion(
                outputs.reshape(-1, config.vocab_size),
                targets.reshape(-1)
            )

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(
            f"Epoch {epoch + 1}/{epochs} "
            f"- Loss: {total_loss / len(loader):.4f}"
        )

    model_path = ROOT / "hikaya_model.pt"
    tokenizer_path = ROOT / "data" / "tokenizer.json"

    torch.save(model.state_dict(), model_path)
    tokenizer.save(tokenizer_path)

    print("اكتملت دورة التدريب التجريبية.")


if __name__ == "__main__":
    train_model()
