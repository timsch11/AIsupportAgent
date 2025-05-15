## Project Overview

This project creates an AI support agent specialized in certain tennis-related inquiries. It uses a small LLM that I adapted to process user support requests. The support agent is embedded into a dashboard that provides a visual interface for relevant API calls. My emails are fetched and analyzed by the AI model and displayed together with a classification of the required task, relevant user data (like username) and a proposed response. Optionally I can still modify the response before I submit the task for automated excecution (done by API calls). 

## Fine-Tuning Approach

### Base Model

- **Model**: Meta-LLaMA 3.2 3B
- **Datatype**: bf16

### Data Collection

Data collection turned out to be quite a challenge as I did not have a lot of past support conversations and public datasets were to general for this specific usecase.
This is why I decided to focus on two specific types of support requests (narrowing down the amount of required data), namely adding users and resetting passwords. Additionally, those are fairly easy to excecute via API calls. In the end I used distillation to generate large parts of the training data and tuned some of those samples by hand.

### Data Processing

- Training data is loaded from CSV format
- System prompt is incorporated with each example
- Conversations follow a structured format with system, user, and assistant roles
- Examples are shuffled and tokenized with padding to max length of 512 tokens
- LLM output is supposed to be a json of relevant user information and a response in a specifcally set format

### Fine-Tuning Approach

I decided to use LoRA for finetuning as the memory usage remains manageable while still providing great finetuning results even without large amounts of data. I kept weights in bf16 precision during training.

## FastAPI Dashboard

The project includes a FastAPI-powered dashboard that serves as the interface for the support system:

- **Interactive UI**: Web-based interface for support staff to monitor and manage queries
- **Request Visualization**: Dashboard displays incoming requests, their status, and AI-suggested responses
- **Manual Override**: Support staff can review and modify AI responses before sending

## API Integration & Automation

The support agent leverages API calls to automate standard support workflows:

- **Automatic Classification**: AI model categorizes incoming requests (account issues, booking problems, general inquiries, etc.)
- **Direct Integration**: Connected to backend services for common operations:
  - Account modifications
  - Booking management (cancellations, modifications)
- **Custom Actions**: Specialized API endpoints for tennis-specific operations

## Setup and Usage

### Requirements

- PyTorch
- Transformers
- PEFT
- Datasets
- Accelerate
- FastAPI
- Uvicorn (for serving the API)

### Fine-Tuning

To fine-tune the model using LoRA:

```bash
python ai/finetuning/finetune_lora.py
```

### Evaluation

To interact with the fine-tuned model:

```bash
python ai/finetuning/eval.py
```

### Running the FastAPI Dashboard

To launch the web dashboard and API server:

```bash
fastapi run app.py
```

Access the dashboard at `http://localhost:8000`

## Response Format

The model is trained to respond with structured JSON containing:
- Category/Action
- Username
- Response text

This structured output facilitates integration with automated systems and API endpoints.

## Automation Workflow

1. User submits a support query
2. AI model processes and classifies the query
3. For standard cases (after approve):
   - System executes relevant API calls automatically
   - Generates appropriate response based on API results
   - Updates user account/bookings as needed
4. For complex cases:
   - Flags for human review
   - Provides suggested responses/actions to support staff

## Notes

This is a personal project designed to explore fine-tuning techniques for specialized domain knowledge. The finetuning approach prioritizes efficient adaptation of the base model while preserving its general capabilities.

The API-driven automation significantly reduces resolution time for common issues while maintaining high-quality responses through the fine-tuned LLM integration.
