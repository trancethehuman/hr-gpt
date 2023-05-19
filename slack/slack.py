import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from ai.ai_functions import load_urls_and_overwrite_index
from ai.ai_agents import initialize_retrieval_agent
from slack.slack_utils import is_dm
from slack.slack_functions import slack_respond_with_agent

load_dotenv()

# Slack App Initialization
bot_token = os.environ["SLACK_BOT_TOKEN"]
app_token = os.environ["SLACK_APP_TOKEN"]
bot_id = os.environ["SLACK_APP_ID"]
app = App(token=bot_token)

# Initialize agent
agent = initialize_retrieval_agent()


# Handle incoming DMs
@app.event("message")
def handle_message_events(event, ack):
    if (is_dm(event)):
        slack_respond_with_agent(agent=agent, ack=ack, app=app, event=event)
    return


@app.event("app_mention")
def handle_mention(event, ack):
    slack_respond_with_agent(agent=agent, ack=ack, app=app, event=event)


@app.command("/upload-new-doc")
def handle_document_upload(body, say, ack):
    ack()
    value = body['text']

    # If user didn't include a URL or URLs, then abort
    if (value == "" or value is None):
        say("Please enter a valid URL to the document!")
        return

    say("I'm uploading a new document! :arrow_up:")

    # Load the URLs into vectorstore
    load_urls_and_overwrite_index(value)

    say("I'm done uploading the document! :white_check_mark:")


def run_slack_app():
    SocketModeHandler(app, app_token).start()
