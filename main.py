import os
from flask import Flask, request, jsonify
import asyncio
import db_utils as db
from bot import send_telegram_notification
from services.message_factory.factory import get_message

app = Flask(__name__)
DATABASE = "messages.db"
AUTH_KEY = os.getenv("AUTH_KEY")  # Load AUTH_KEY from environment variables

# Example request for /sendMessage endpoint:
# {
#     "state": "occupy",        # Required: Must be "occupy" or "empty"
#     "bot": "bot_token",       # Required: Telegram bot token
#     "notification": true,     # Required: Whether to send with notification
#     "chatId": "123456789"    # Required: Telegram chat ID to send message to
# }
#
# Response format:
# Success (200):
# {}
#
# Error (400, 401, 500, 503):
# {
#     "error": "Error message",
#     "details": "Detailed error message"  # Only included for some errors
# }

# Async endpoint to handle messages
@app.route("/sendMessage", methods=["POST"])
async def send_message():
    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header != AUTH_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Validate JSON payload - get_json() is synchronous
    data = request.get_json()  # Removed await
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
        message = get_message(state)
        await send_telegram_notification(bot, chat_id, notification, message)
    except FileNotFoundError as e:
        app.logger.error(f"Message file not found: {str(e)}")
        return jsonify({
            "error": "Configuration error",
            "details": "Message template file not found"
        }), 500
    except ValueError as e:
        app.logger.error(f"Invalid message file: {str(e)}")
        return jsonify({
            "error": "Configuration error", 
            "details": "Message template file is empty"
        }), 500
    except aiohttp.ClientError as e:
        app.logger.error(f"Telegram API error: {str(e)}")
        return jsonify({
            "error": "Failed to send message",
            "details": "Error connecting to Telegram API"
        }), 503
    except Exception as e:
        app.logger.error(f"Unexpected error sending message: {str(e)}")
        return jsonify({
            "error": "Internal server error",
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