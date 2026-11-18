
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv #Helper module to access secret keys in program
import mysql.connector
from werkzeug.security import generate_password_hash


load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

#database configuration loaded from .env
ai_chatbot_db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

#connection helper
def get_connection():
    return mysql.connector.connect(**ai_chatbot_db_config)


app = Flask(__name__)


def clean_text(data, field):
    """Return the field as a stripped string, or None if missing or not text."""
    value = data.get(field)
    if not isinstance(value, str):
        return None
    return value.strip()


def check_required(data, fields):
    """Return an error message for the first missing field, else None."""
    for field in fields:
        if not clean_text(data, field):
            return f"{field} is required"
    return None

@app.route("/api/health", methods=['GET'])
def health_check():
    """Health check: confirms the server is running"""
    return jsonify({"status": "ok"}), 200

@app.route("/api/signup", methods=["POST"])
def signup():
    """Create a new user account."""
    # silent=True returns None on bad JSON instead of crashing; "or {}" gives an empty dict
    data = request.get_json(silent=True) or {}

    # Cheap checks run first so invalid requests never touch the database
    error = check_required(data, ["name", "email"])
    if error:
        return jsonify({"error": error}), 400

    name = clean_text(data, "name")
    email = clean_text(data, "email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    # isinstance guards against non-text input such as a number
    if not isinstance(password, str) or len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    # Confirm password is only a frontend check; it is never stored
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Store only the salted hash, never the plain password
    hashed = generate_password_hash(password)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # %s placeholders keep user input separate from the SQL (blocks SQL injection)
        cursor.execute(
            "INSERT INTO `users`(`name`, `email`, `password_hash`) VALUES (%s, %s, %s)",
            (name, email, hashed),
        )
        conn.commit()  # without commit, the insert is discarded
        return jsonify({"message": "Account created"}), 201
    except mysql.connector.IntegrityError:
        # UNIQUE rule on name or email was broken (MySQL error 1062)
        return jsonify({"error": "Name or email already exists"}), 409
    finally:
        # Runs on success and on failure, so connections never pile up
        cursor.close()
        conn.close()

if __name__ =="__main__":
    app.run(debug=True)
    



