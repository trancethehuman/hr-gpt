import os
import random
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from ai_agents import get_agent_zero_shot_response
from ai_tools import tool_describe_skills, tool_retrieve_company_info, tool_calculate_stock_options
from consts import thinking_thoughts
from utils import extract_messages

load_dotenv()

# Slack App Initialization
bot_token = os.environ["SLACK_BOT_TOKEN"]
app_token = os.environ["SLACK_APP_TOKEN"]
app = App(token=bot_token)


# Handle incoming DMs or channel messages
@app.event("message")
def handle_message_events(event, ack, say):
    # Acknowledge user's message
    ack()
    say(random.choice(thinking_thoughts))

    # Get the conversation history (last 10 messages)
    messages_history = []
    channel = event["channel"]
    conversation_history = app.client.conversations_history(
        channel=channel, limit=10)
    messages_history.extend(extract_messages(conversation_history))

    # Give the bot context of about the user (first name)
    user_id = event["user"]
    user_first_name = app.client.users_info(
        user=user_id)['user']['profile']['first_name']  # type: ignore
    messages_history.append(
        {"type": "user", "message": f"""My name is {user_first_name}"""})

    # Generate a response
    user_query = event["text"]
    agent_tools = [tool_retrieve_company_info(
    ), tool_describe_skills(), tool_calculate_stock_options()]
    response = get_agent_zero_shot_response(
        user_query, tools=agent_tools, messages_history=messages_history)

    # Replace acknowledgement message with actual response
    if response and conversation_history["messages"]:
        last_message_id = conversation_history["messages"][0]["ts"]
        app.client.chat_update(
            channel=channel,
            ts=last_message_id,
            text=response,
        )

        # Reaction emojis to get feedback from user
        reactions = ["thumbsup", "thumbsdown"]
        for reaction in reactions:
            app.client.reactions_add(
                channel=channel,
                timestamp=last_message_id,
                name=reaction,
            )


# Handle criticisms or praise
@app.event("reaction_added")
def handle_feedback(event, say):
    if (event['reaction'] == "+1"):
        say(f"Thanks for your feedback! :{event['reaction']}:")
    if (event['reaction'] == "-1"):
        say(f"I'll do better next time! :disappointed:")
    # TODO: save user's feedback to Google Sheets or something!


@app.command("/upload-new-doc")
def handle_some_command(body, say, ack):
    ack()
    value = body['text']
    if (value == "" or value == None):
        say("Please enter a valid URL to the document!")
        return
    print(body['text'])
    say("I'm uploading a new document! :robot_face:")

    # Give LangChain doc loader the URL

    say("I'm done uploading the document! :robot_face:")


# Start Slack app
if __name__ == "__main__":
    SocketModeHandler(app, app_token).start()
