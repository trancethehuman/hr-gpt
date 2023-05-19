import random
from consts import thinking_thoughts


def is_dm(message) -> bool:
    # Check if the message is a DM by looking at the channel ID
    if message['channel'].startswith('D'):
        return True
    return False


def get_random_thinking_message():
    return random.choice(thinking_thoughts)


def send_slack_message_and_return_message_id(app, channel, message: str):
    response = app.client.chat_postMessage(
        channel=channel,
        text=message)
    if response["ok"]:
        message_id = response["message"]["ts"]
        return message_id
    else:
        return ("Failed to send message.")
