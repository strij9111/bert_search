import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer


device = 'cuda' if torch.cuda.is_available() else 'cpu'

tokenizer = GPT2Tokenizer.from_pretrained("ai-forever/rugpt3large_based_on_gpt2")
model = GPT2LMHeadModel.from_pretrained("ai-forever/rugpt3large_based_on_gpt2").to(device)

text = "как называется фильм про ограбление с Беном Аффликом"
input_ids = tokenizer.encode(text, return_tensors="pt").to(device)
input_ids = torch.nn.functional.pad(input_ids, (0, 100 - input_ids.shape[-1]), value=tokenizer.pad_token_id).to(device)
out = model.generate(
    input_ids,
    min_length=100,
    max_length=512,
    eos_token_id=5,
    top_k=10,
    top_p=0.0,
    no_repeat_ngram_size=5
)
generated_text = list(map(tokenizer.decode, out))[0]
print(generated_text)
