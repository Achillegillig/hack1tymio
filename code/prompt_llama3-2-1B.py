from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# Specify the model name
model_name = "meta-llama/Llama-3.2-1B-Instruct"
model_path = "/data/extra/agillig/llama/Llama-3.2-1B-Instruct"
# Download the model and tokenizer
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Save the model and tokenizer to a local directory
model.save_pretrained(model_path)
tokenizer.save_pretrained(model_path)
device = 0 if torch.cuda.is_available() else -1
print(device)
# Create the pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=device
)

msg = "Hey Llama, How do I make Jonathan understand Neuroscience ?"
print(msg)
messages = [ {"role": "user", "content": msg} ]

outputs = pipe(messages,
               max_new_tokens=256,
               do_sample=True,)

assistant_response = outputs[0]['generated_text'][-1]["content"]
print(assistant_response)