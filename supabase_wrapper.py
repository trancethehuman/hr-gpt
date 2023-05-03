import os
from dotenv import load_dotenv
from supabase import create_client, Client  # type: ignore

# Load .env variables
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)  # type: ignore


def write_message_log(user_name: str, message: str):
    supabase.table('logs').insert(
        {"user_name": user_name, "message": message}).execute()
