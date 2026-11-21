
from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv #Helper module to access secret keys in program
import mysql.connector
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from persona import BOT_PERSONA

load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")
openrouter_model = os.getenv("OPENROUTER_MODEL")

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

def get_current_user_id():
    """Return the user id from the Bearer token, or None if missing or invalid."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header[len("Bearer "):]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return int(payload["sub"])
    except jwt.InvalidTokenError:
        return None

def write_log(user_id, event_type, status_code):
    """Record one event. Never raises, so a logging failure can't break a request."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO logs (user_id, event_type, path, method, status_code) VALUES (%s, %s, %s, %s, %s)",
                (user_id, event_type, request.path, request.method, status_code),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    except mysql.connector.Error as exc:
        print("Audit log failed:", repr(exc))

@app.route("/api/me", methods=["GET"])
def me():
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Authentication required"}), 401
    return jsonify({"user_id": user_id}), 200


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

@app.route("/api/signin", methods=['POST'])
def signin():
    """Sign a user in with name and password."""
    data = request.get_json(silent=True) or {}

    error = check_required(data, ["name", "password"])
    if error:
        return jsonify({"error": error}), 400

    name = clean_text(data, "name")
    password = data.get("password")

    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, name, password_hash FROM users WHERE name = %s",
            (name,),
        )
        row = cursor.fetchone()

        #Create on token on signin

        if row is None or not check_password_hash(row["password_hash"], password):
            write_log(None, "login_failed", 401)
            return jsonify({"error": "Invalid name or password"}), 401

        token = jwt.encode(
            {"sub": str(row["id"]), "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            JWT_SECRET,
            algorithm="HS256",
        )

        write_log(row["id"], "login", 200)
        return jsonify({"message": "Signed in", "token": token}), 200

    finally:
        cursor.close()
        conn.close()



@app.route("/api/chat", methods=['POST'])
def chat():
    """Send a message to the AI bot and return its reply."""
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Authentication required"}), 401
    

    data = request.get_json(silent=True) or {}
    message= clean_text(data, "message")
    if not message:
        return jsonify({"error":"Message is required"}), 400

    if len(message) > 2000:
        return jsonify({"error":"Message is too long"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY created_at DESC, id DESC LIMIT 10",
            (user_id,),
        )
        rows = cursor.fetchall()
        rows.reverse()
        history = [{"role": r["role"], "content": r["content"]} for r in rows]

        messages = [{"role": "system", "content": BOT_PERSONA}] + history
        messages.append({"role": "user", "content": message})

        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}", 
                    "Content-Type": "application/json"
                },
                json={
                    "model": openrouter_model, 
                    "messages": messages
                },
                timeout=30,
            )
            resp.raise_for_status()
            reply = resp.json()["choices"][0]["message"]["content"]

        except (requests.RequestException, KeyError, IndexError) as exc:
            write_log(user_id, "chat", 502)
            return jsonify({"error": "AI service unavailable"}), 502
        
        cursor.executemany(
            "INSERT INTO chat_history (user_id, role, content) VALUES (%s, %s, %s)",
            [
                (user_id, "user", message),
                (user_id, "assistant", reply),
            ],
        )
        conn.commit()
        write_log(user_id, "chat", 200)
        return jsonify({"reply": reply}), 200
            
    finally:
        cursor.close()
        conn.close()

@app.route("/api/history", methods=["GET"])
def history():
    """Return the signed-in user's orders, oldest first."""
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Authentication required"}), 401

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, role, content, created_at FROM chat_history WHERE user_id = %s ORDER BY created_at ASC, id ASC",
            (user_id,),
        )
        rows = cursor.fetchall()
        for row in rows:
            row["created_at"] = row["created_at"].isoformat()
        return jsonify({"messages": rows}), 200
    finally:
        cursor.close()
        conn.close()




@app.route("/api/signout", methods=["POST"])
def signout():
    """Record that the signed-in user signed out."""
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"error": "Authentication required"}), 401

    write_log(user_id, "logout", 200)
    return jsonify({"message": "Signed out"}), 200



if __name__ =="__main__":
    app.run(debug=True)
    



