
from flask import Flask, jsonify
import os
from dotenv import load_dotenv #Helper module to access secret keys in program


load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")


ai_chatbot_db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}



app = Flask(__name__)

@app.route("/api/health", methods=['GET'])
def health_check():
    """Health check: confirms the server is running"""
    return jsonify({"status": "ok"}), 200

if __name__ =="__main__":
    app.run(debug=True)



