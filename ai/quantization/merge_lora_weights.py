from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import torch

base_model_name = "meta-llama/Llama-3.2-3B"
lora_model_path = "ai/model_r16_b2_lr"

# Load the base model in bf16
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name, 
    torch_dtype=torch.bfloat16, 
    device_map="auto"
)

# Load the LoRA adapter and merge it
model = PeftModel.from_pretrained(base_model, lora_model_path)
model = model.merge_and_unload()  # This merges LoRA weights into the base model
model.save_pretrained("ai/model/model_merged")
