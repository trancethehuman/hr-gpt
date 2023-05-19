from ai.ai_agents import get_agent_response
from slack.slack_utils import get_random_thinking_message, send_slack_message_and_return_message_id
from utils import extract_messages
from consts import demo_company_name


def slack_respond_with_agent(agent, event, ack, app):
    """
    This function takes a Slack message event and respond with a LLM-generated response
    """

    channel = event["channel"]

    # Acknowledge user's message
    ack()
    ack_message_id = send_slack_message_and_return_message_id(
        app=app, channel=channel, message=get_random_thinking_message())

    # Get the conversation history (last 5 messages)
    messages_history = []
    conversation_history = app.client.conversations_history(
        channel=channel, limit=5)
    messages_history.extend(extract_messages(conversation_history))

    # Write message log to Supabase
    # write_message_log(user_name=user_first_name, message=event["text"])

    # Give the bot context of about the user (first name)
    user_id = event["user"]
    user_first_name = app.client.users_info(
        user=user_id)['user']['profile']['first_name']  # type: ignore
    messages_history.append(
        {"type": "user", "message": f"""My name is {user_first_name}"""})
    messages_history.append(
        {"type": "AI", "message": f"""I'm a HR assistant at {demo_company_name} and I answer questions cheerfully."""})

    # Generate an LLM response using agent
    user_query = event["text"]

    response = get_agent_response(
        agent=agent, query=user_query, messages_history=messages_history)

    blocks = [
        {
            "type": "section",
            "text": {
                    "type": "mrkdwn",
                    "text": response
            },
        },
        {
            "type": "actions",
            "block_id": "actionblock789",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "👍"
                    },
                    "style": "primary",
                    "value": "click_me_456"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "👎"
                    },
                    "style": "primary",
                    "value": "click_me_456"
                }
            ]
        }
    ]

    # Replace acknowledgement message with actual response
    app.client.chat_update(
        channel=channel,
        text=response,
        ts=ack_message_id,
        blocks=blocks
    )

    # Write message log to Supabase
    # write_message_log("AI", response)
