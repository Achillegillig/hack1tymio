from flask import Flask, request, jsonify, send_from_directory
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

import find_port
import os
import socket

print(socket.gethostname())

app = Flask(__name__)

# Load the model and tokenizer
model_name = "meta-llama/Llama-3.2-1B-Instruct"
model_path = "/data/extra/agillig/llama/Llama-3.2-3B-Instruct"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

device = 0 if torch.cuda.is_available() else -1

port = find_port.find_open_port()
print(f"Available port: {port}")

# Create the pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=device
)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    messages = data.get('messages', [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    outputs = pipe(messages, max_new_tokens=256, do_sample=True)
    assistant_response = outputs[0]['generated_text'][-1]["content"]
    return jsonify({"generated_text": assistant_response})

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(__file__), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)