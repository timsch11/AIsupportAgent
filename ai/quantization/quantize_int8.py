
from transformers import AutoModelForCausalLM


model = "ai/model_merged"

model = AutoModelForCausalLM.from_pretrained(
    model,
    load_in_8bit=True,
    device_map="auto"
)

model.save_pretrained("ai/model_q_int8")
