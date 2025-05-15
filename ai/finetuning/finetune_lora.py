from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
from datasets import load_dataset
from accelerate import Accelerator
import torch

# basemodel
model_name = "meta-llama/Llama-3.2-3B"

# Load basemodel and its tokenizer
tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=model_name)

# set correct chat template for llama 3.2 3b
tokenizer.chat_template = '''{% for message in messages %}{% if message['role'] == 'user' %}[INST] {{ message['content'] }} [/INST]{% elif message['role'] == 'assistant' %}{{ message['content'] }}{% endif %}{% endfor %}'''

model = AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path=model_name,
    return_dict=True,
    low_cpu_mem_usage=True,
    torch_dtype=torch.bfloat16,     # base model is in bf16 precision
    device_map="cuda",              # cuda for batch size <3 "auto" to use second gpu for larger batch sizes
    trust_remote_code=False,
)

# set padding token
if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id
if model.config.pad_token_id is None:
    model.config.pad_token_id = model.config.eos_token_id

# load and shuffle training data from csv file (actually semikolon seperated) 
dataset = load_dataset("csv", data_files="ai/data/formatted_data_final.csv", delimiter=";", split="train")
dataset = dataset.shuffle()

# read system prompt 
with open("ai/data/system_prompt2.txt", 'r') as f:
    system_prompt = f.read()

def preprocess(examples):
    # first apply chat template to format conversations properly
    conversations = [
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req},
            {"role": "assistant", "content": resp}
        ]
        for req, resp in zip(examples["request"], examples["response"])
    ]
    
    # apply chat template without tokenizing for now
    prompts = [
        tokenizer.apply_chat_template(
            conversation,
            tokenize=False,
            add_generation_prompt=True
        )
        for conversation in conversations
    ]
    
    # tokenize
    tokenized_inputs = tokenizer(
        prompts,
        truncation=True,
        padding="max_length",   # apply padding to shorter batch samples to match the lognest sample
        max_length=512,
        return_tensors="pt"
    )
    
    return {
        "input_ids": tokenized_inputs["input_ids"],
        "attention_mask": tokenized_inputs["attention_mask"],
        "labels": tokenized_inputs["input_ids"].clone()  # For causal LM, labels are the same as inputs
    }

# apply chat template and tokenize
tokenized_datasets = dataset.map(
    preprocess,
    batched=True,
    remove_columns=dataset.column_names
)

# Set up lora config for peft
lora_config = LoraConfig(
    r=16,                                           # rank
    lora_alpha=32,                                  # scaling factor
    target_modules=["q_proj", "v_proj"],            # Modules to apply lora
    task_type=TaskType.CAUSAL_LM,
)

# Apply lora to the pre-trained model using peft
model = get_peft_model(model, lora_config)

# Use the accelerator for mixed-precision and distributed training
#accelerator = Accelerator()

# Set up the Trainer and training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=6,
    per_device_train_batch_size=2,
    logging_dir="./logs",
    save_steps=10_000,
    logging_steps=200,
    save_total_limit=3,
    bf16=True,
    learning_rate=0.0002
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
    tokenizer=tokenizer,
)

# Start training
trainer.train()

trainer.save_model("ai/model_r16_b2_lr")
