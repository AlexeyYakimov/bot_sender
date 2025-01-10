import os
from flask import Flask, request, jsonify
import asyncio
import db_utils as db
from bot import send_telegram_notification

app = Flask(__name__)
DATABASE = "messages.db"
AUTH_KEY = os.getenv("AUTH_KEY")  # Load AUTH_KEY from environment variables

# Async endpoint to handle messages
@app.route("/sendMessage", methods=["POST"])
async def send_message():
    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header != AUTH_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Validate JSON payload
    data = await request.get_json()
    required_fields = {"state", "bot", "notification", "chatId"}
    if not data or not required_fields.issubset(data.keys()):
        return jsonify({"error": "Invalid request, missing fields"}), 400

    state = data.get("state")
    bot = data.get("bot")
    notification = data.get("notification")
    chat_id = data.get("chatId")

    # Validate "state" field
    if not validate_state(state):
        return jsonify({"error": 'Field "state" must be "occupy" or "empty"'}), 400

    # Save to the database
    await db.save_data_to_db(bot, chat_id, notification, state)

    # Send notification to Telegram
    try:
        message = f"State changed to: {state}"
        await send_telegram_notification(bot, chat_id, state, notification, message)
    except Exception as e:
        app.logger.error(f"Error sending Telegram message: {str(e)}")
        return jsonify({
            "error": "Failed to send Telegram message",
            "details": str(e)
        }), 500

    return jsonify({"status": "success", "message": "Message saved"})


def validate_state(state):
    return state in {"occupy", "empty"}


if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    # Ensure the AUTH_KEY is set
    if not AUTH_KEY:
        raise RuntimeError("AUTH_KEY environment variable not set")

    # Initialize database before starting server
    db.init_db()

    config = Config()
    config.bind = [os.getenv("HOST_PORT", "127.0.0.1:8000")]
    asyncio.run(serve(app, config))