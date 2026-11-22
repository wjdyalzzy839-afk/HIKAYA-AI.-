import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from .model import HikayaAI, HikayaConfig
from .tokenizer import HikayaTokenizer


class HikayaDataset(Dataset):
    def __init__(self, texts, tokenizer, seq_len=64):
        self.samples = []
        self.seq_len = seq_len

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


def train_model(texts, epochs=5, batch_size=4):
    tokenizer = HikayaTokenizer()
    tokenizer.fit(texts)

    dataset = HikayaDataset(texts, tokenizer)

    if not len(dataset):
        raise ValueError("لا توجد نصوص كافية للتدريب.")

    config = HikayaConfig
    config.vocab_size = max(4, len(tokenizer.token_to_id))

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

    torch.save(model.state_dict(), "hikaya_model.pt")
    tokenizer.save("data/tokenizer.json")

    print("اكتمل التدريب التجريبي.")


if __name__ == "__main__":
    sample_texts = [
        "التاريخ سجل أحداث الشعوب.",
        "تقع اليمن في جنوب غرب شبه الجزيرة العربية.",
        "الحضارات القديمة جزء مهم من تاريخ البشرية."
    ]

    train_model(sample_texts)
