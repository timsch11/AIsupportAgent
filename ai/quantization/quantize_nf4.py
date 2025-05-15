
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch


model = "ai/model_merged"

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True, 
    bnb_4bit_compute_dtype=torch.bfloat16,      # Match original dtype
    bnb_4bit_quant_type="nf4"                   # Normal Float 4 (best for LLMs)
)

# Reload the model with 4-bit quantization
model = AutoModelForCausalLM.from_pretrained(
    model, 
    quantization_config=quantization_config, 
    device_map="auto"
)

model.save_pretrained("ai/model_quantized")
