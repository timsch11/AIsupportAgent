from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

import json
import logging


# setup logger for this file
LOGGER = logging.getLogger(__name__)

base_model_name = "meta-llama/Llama-3.2-3B"
finetuned_model_path = "C:\\Users\\timsc\\Desktop\\projects\\tennisAut\\supportAgent\\model\\bf16"


CHAT_TEMPLATE = '''{% for message in messages %}{% if message['role'] == 'user' %}[INST] {{ message['content'] }} [/INST]{% elif message['role'] == 'assistant' %}{{ message['content'] }}{% endif %}{% endfor %}'''

with open("ai/data/system_prompt2.txt", 'r') as f:
        SYSTEM_PROMPT = f.read()

class Model:
    def __init__(self, systemPrompt: str=SYSTEM_PROMPT, preload=False):
        # load if preload flag is set
        if preload:
            self.load_model_and_tokenizer()

        self.loaded = preload
        self.system_prompt = systemPrompt


    def load_model_and_tokenizer(self):
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        #self.tokenizer = AutoTokenizer.from_pretrained(finetuned_model_path)
        
        # Set chat template
        self.tokenizer.chat_template = CHAT_TEMPLATE
        
        # Load full model
        self.model = AutoModelForCausalLM.from_pretrained(finetuned_model_path, device_map="cpu", torch_dtype=torch.bfloat16)

        # log
        LOGGER.info("Model and tokenizer successfully loaded")


    def generate_response(self, user_input, max_length=512) -> dict[str]:
        # log
        LOGGER.info(f"Generating response for: '{user_input}'")

        # load model if not loaded yet
        if not self.loaded:
            # log
            LOGGER.info("Model and tokenizer need to be loaded")

            self.load_model_and_tokenizer()

        else:
            # log
            LOGGER.info("Model and tokenizer already loaded")

        # Format the conversation with system prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # Apply chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate response
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            temperature=0.6,
            top_p=0.9,
            num_return_sequences=1,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        )
        
        # Decode and return response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # use response only
        response = response.split(sep="[/INST]")[-1]

        # parse json response
        try:
            result = json.loads(response)

            # log
            LOGGER.info(f"Model generated parseable response: '{result}'")

            return result
        
        except Exception as exc:
            # log
            LOGGER.error("Model did not respond in suitable json format", exc_info=exc)

            raise exc


if __name__ == '__main__':
    model = Model()
    print(model.generate_response("Hallo, Kannst du mein Passwort zurücksetzen. Viele Grüße Katja Schule"))