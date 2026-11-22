import torch

from hikaya_ai.model import HikayaAI, HikayaConfig
from hikaya_ai.tokenizer import HikayaTokenizer


def test_model_output_shape():
    config = HikayaConfig
    config.vocab_size = 100
    model = HikayaAI(config)

    tokens = torch.randint(0, 100, (2, 16))
    output = model(tokens)

    assert output.shape == (2, 16, 100)


def test_tokenizer_encode_decode():
    tokenizer = HikayaTokenizer()

    text = "تاريخ اليمن عريق"
    tokenizer.fit([text])

    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert len(encoded) > 0
    assert decoded == text
