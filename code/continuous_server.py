from flask import Flask, request, jsonify, send_from_directory
import os
from ollama import Llama, Tokenizer

app = Flask(__name__)

# Initialize the Llama model and tokenizer
model = Llama(model_name="llama-3.2")
tokenizer = Tokenizer(model_name="llama-3.2")
device = "cuda" if torch.cuda.is_available() else "cpu"

# Keep chat history
chat_history = []

@app.route('/api/generate', methods=['POST'])
def generate():
    global chat_history
    data = request.json
    messages = data.get('messages', [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    # Add new messages to chat history
    chat_history.extend(messages)

    # Generate response using the chat history
    inputs = tokenizer(chat_history, return_tensors="pt", padding=True, truncation=True)
    inputs = inputs.to(device)
    outputs = model.generate(inputs, max_new_tokens=256, do_sample=True)
    assistant_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Update chat history with the assistant's response
    chat_history.append({"role": "assistant", "content": assistant_response})

    return jsonify({"generated_text": assistant_response})

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(__file__), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)