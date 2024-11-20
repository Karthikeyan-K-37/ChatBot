# web.py
from flask import Flask, render_template, request, jsonify
from Main import process_message, state

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form.get("user_input")
    if user_input.lower() == "goodbye":
        return jsonify({"response": "Goodbye!"})

    # Process the user's input using the Main.py logic
    result = process_message(user_input, state)
    
    bot_message = result["messages"][0]["content"]
    return jsonify({"response": bot_message})

if __name__ == "__main__":
    app.run(debug=True)
