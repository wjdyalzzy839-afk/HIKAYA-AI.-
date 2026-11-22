import torch
import torch.nn as nn


class HikayaConfig:
    vocab_size = 1000
    embedding_dim = 128
    num_heads = 4
    num_layers = 2
    max_seq_len = 256


class HikayaAI(nn.Module):
    def __init__(self, config=HikayaConfig):
        super().__init__()

        self.token_embedding = nn.Embedding(
            config.vocab_size,
            config.embedding_dim
        )

        self.position_embedding = nn.Embedding(
            config.max_seq_len,
            config.embedding_dim
        )

        layer = nn.TransformerEncoderLayer(
            d_model=config.embedding_dim,
            nhead=config.num_heads,
            batch_first=True
        )

        self.transformer = nn.TransformerEncoder(
            layer,
            num_layers=config.num_layers
        )

        self.output = nn.Linear(
            config.embedding_dim,
            config.vocab_size
        )

    def forward(self, tokens):
        batch_size, seq_len = tokens.shape

        positions = torch.arange(
            seq_len,
            device=tokens.device
        )

        x = (
            self.token_embedding(tokens)
            + self.position_embedding(positions)
        )

        mask = torch.triu(
            torch.ones(seq_len, seq_len, device=tokens.device),
            diagonal=1
        ).bool()

        x = self.transformer(x, mask=mask)

        return self.output(x)
