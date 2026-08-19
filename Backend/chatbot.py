import os
import threading
from flask import Flask, request, jsonify, render_template
from groq import Groq
from google.colab.output import eval_js

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found. Run the secrets cell above first.")

client = Groq(api_key=api_key)
model = "openai/gpt-oss-120b"

conversation_history = [
    {"role": "system", "content": (
        "You are Abhradeep, a 19-year-old Computer Science Engineering (CSE) student. "
        "You are chatting with a visitor on your personal website as yourself — not as a "
        "generic AI assistant. Speak in first person, be friendly, casual, and approachable. "
        "You can talk about your interests in CSE, coding, college life, tech, or anything else "
        "the visitor brings up, as if you're genuinely having a conversation with them. "
        "Keep responses natural and conversational, not robotic."
    )}
]

app = Flask(__name__)

PORT = 8001   # change this if you want a different port

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat")
def chat_page():
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
def chat_api():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Please type something."})

    conversation_history.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=conversation_history
        )
        output_text = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": output_text})
        return jsonify({"reply": output_text})

    except Exception as e:
        conversation_history.pop()
        return jsonify({"reply": f"Sorry, I encountered an error: {e}"})

def run_app():
    app.run(port=PORT)

threading.Thread(target=run_app).start()

url = eval_js(f"google.colab.kernel.proxyPort({PORT})")
print(f"Click here to open your web app:\n{url}")
