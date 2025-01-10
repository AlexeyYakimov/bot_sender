import aiohttp
import asyncio

async def send_telegram_notification(bot_token, chat_id, state, notification, message):
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    async def try_send_message():
        async with aiohttp.ClientSession() as session:
            async with session.post(telegram_url, json={
                "chat_id": chat_id,
                "text": message,
                "disable_notification": not notification
            }) as response:
                if response.status != 200:
                error_data = await response.json()
                return False, error_data
            return True, None

    # Try to send message with one retry
    success, error_data = await try_send_message()
    if not success:
        # Wait briefly before retry
        await asyncio.sleep(1)
        success, error_data = await try_send_message()
        
        if not success:
            raise Exception(f"Failed to send Telegram message after retry: {error_data}")

    return jsonify({"status": "success", "message": "Message saved"})
