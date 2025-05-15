import os
import json

import torch

from transformers import LlamaConfig, LlamaTokenizer, LlamaForCausalLM, AutoTokenizer
import gc


path = "/home/ts/.llama/checkpoints/Llama3.2-3B"

config_path = "params.json"

# Load the JSON file
with open(os.path.join(path, config_path), "r") as f:
    config = json.load(f)

print("loaded config file")
gc.collect()

hf_config = LlamaConfig(
    hidden_size=config["dim"],
    num_attention_heads=config["n_heads"],
    num_hidden_layers=config["n_layers"],
    intermediate_size=config["dim"] * 4,
    rms_norm_eps=config["norm_eps"],
    vocab_size=config["vocab_size"]
)

print("loaded config")
gc.collect()

# Save config to use later
# hf_config.save_pretrained("ai/model/converted_llama3")

# Load the model structure
torch.set_default_dtype = torch.float16
torch.set_default_device = torch.device("cuda")

tensor1 = torch.tensor([0.0, 0.0])
print(tensor1.dtype)
exit()

with torch.no_grad():
    model = LlamaForCausalLM(hf_config)
    #model = LlamaForCausalLM(hf_config, torch_dtype=torch.float16).to("cuda")

    print("loaded model from config")
    gc.collect()

    # Load the .pth weights
    pth_path = os.path.join(path, "consolidated.00.pth")

    gc.collect()

    # Load the weights into the model
    model.load_state_dict(torch.load(pth_path, map_location="cuda"))

    print("loaded state dict")
    gc.collect()

    # Save the model in Hugging Face format
    model.save_pretrained("ai/model")
    print("Model successfully loaded and saved in Hugging Face format!")
    gc.collect()

del model

# Load tokenizer from tokenizer.model
tok_path = os.path.join(path)
tokenizer = AutoTokenizer.from_pretrained(tok_path, legacy=False, trust_remote_code=True)

print("loaded tokenizer")
gc.collect()

# set pad token
tokenizer.pad_token = tokenizer.eos_token

gc.collect()

# Save tokenizer in Hugging Face format
tokenizer.save_pretrained("ai/model")