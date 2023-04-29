from datetime import datetime, timedelta


def format_sources(unformatted_sources, max_displaying_sources: int):
    """
    The function takes a list of LangChain QARetrieval sources (list of dictionaries) and max number of sources to return, extracts the correct key from each dictionary to get the source's name, cleans the
    extracted data, formats it, and returns all as a string for displaying.
    """

    sources = []

    # Grab only the actual sources' names
    for source in unformatted_sources:
        sources.append(source.metadata)

    # Limit number of sources to display
    sources = sources[:max_displaying_sources]

    # Remove the prefix from the sources
    cleaned_prefix_sources = [item['source'].replace(
        "input_data\\gitlab_handbook\\", "") for item in sources]

    # Make the sources list look like a numbered list
    formatted_sources = '\n'.join(
        [f"{i+1}. {item}" for i, item in enumerate(cleaned_prefix_sources)])

    return formatted_sources


def extract_messages(conversation_history):
    """
    The function extracts messages from a Slack conversation history and categorizes them as either AI or user
    messages.
    """
    messages = []
    for message in conversation_history['messages']:
        if 'bot_id' in message:
            messages.append({"type": "AI", "message": message['text']})
        elif 'user' in message:
            messages.append({"type": "user", "message": message['text']})

    return messages


def calculate_vesting(start_date, total_shares, vesting_schedule):
    """
    Calculates the vesting schedule for a given employee based on the start date, total shares, and vesting schedule.
    """
    vesting_details = []
    cumulative_percentage = 0
    for percentage in vesting_schedule:
        shares_to_vest = int(total_shares * percentage)
        cumulative_percentage += percentage
        vesting_date = datetime.strptime(
            start_date, '%Y-%m-%d') + timedelta(days=365*cumulative_percentage)
        vesting_details.append(
            (vesting_date.strftime('%Y-%m-%d'), shares_to_vest))

    results = vesting_details

    return results
