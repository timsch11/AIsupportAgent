from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

import json

import torch

def load_model_and_tokenizer():
    base_model_name = "meta-llama/Llama-3.2-3B"
    peft_model_path = "ai/model_r16_b2_lr"
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    
    # Set chat template
    tokenizer.chat_template = '''{% for message in messages %}{% if message['role'] == 'user' %}[INST] {{ message['content'] }} [/INST]{% elif message['role'] == 'assistant' %}{{ message['content'] }}{% endif %}{% endfor %}'''
    
    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.bfloat16,
        device_map="cuda"
    )
    
    # Load LoRA weights
    model = PeftModel.from_pretrained(base_model, peft_model_path)
    
    return model, tokenizer

def generate_response(model, tokenizer, system_prompt, user_input, max_length=512):
    # Format the conversation with system prompt
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    # Apply chat template
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Generate response
    outputs = model.generate(
        **inputs,
        max_length=max_length,
        temperature=0.6,
        top_p=0.9,
        num_return_sequences=1,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id
    )
    
    # Decode and return response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

def main():
    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer()
    
    # Load system prompt
    with open("ai/data/system_prompt2.txt", 'r') as f:
        system_prompt = f.read()
    
    # Interactive loop
    print("Model loaded! Type 'quit' to exit.")
    while True:
        user_input = input("\nYour question: ")
        if user_input.lower() == 'quit':
            break
            
        response = generate_response(model, tokenizer, system_prompt, user_input).split(sep="[/INST]")[-1]
        try:
            response = json.loads(response)
            print(f"Aktion: {response["Kategorie"]}")
            print(f"Benutzername: {response["Benutzername"]}")
            print(f"Antwort: {response["Antwort"]}")
        except:
            print(response)

if __name__ == "__main__":
    main()
    