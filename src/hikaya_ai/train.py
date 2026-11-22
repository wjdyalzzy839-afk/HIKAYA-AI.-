import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from model import HikayaAI, HikayaConfig
from tokenizer import HikayaTokenizer


class HikayaDataset(Dataset):
    def __init__(self, texts, tokenizer, seq_len=64):
        self.samples = []

        for text in texts:
            ids = tokenizer.encode(text)

            if len(ids) < 2:
                continue

            for start in range(0, len(ids) - 1, seq_len):
                chunk = ids[start:start + seq_len + 1]

                if len(chunk) >= 2:
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

    if len(dataset) == 0:
        raise ValueError("لا توجد نصوص كافية للتدريب.")

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True
    )

    config = HikayaConfig
    config.vocab_size = max(4, len(tokenizer.token_to_id))

    model = HikayaAI(config)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=0.0003
    )

    criterion = nn.CrossEntropyLoss()
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

        average_loss = total_loss / len(loader)
        print(
            f"Epoch {epoch + 1}/{epochs} "
            f"- Loss: {average_loss:.4f}"
        )

    torch.save(model.state_dict(), "hikaya_model.pt")
    tokenizer.save("data/tokenizer.json")

    print("اكتملت دورة التدريب وحُفظ النموذج.")


if __name__ == "__main__":
    sample_texts = [
        "التاريخ هو سجل الأحداث التي عاشتها الشعوب.",
        "تقع اليمن في جنوب غرب شبه الجزيرة العربية.",
        "تعد الحضارات القديمة جزءا مهما من تاريخ البشرية."
    ]

    train_model(sample_texts)
