# main.py

import os
import json
import time
import webbrowser
from connections.google.google_oauth_client import GoogleOAuthClient
from modules.app_actions.discord.executive_director_bot import bot
from agents.base_agent import BaseAgent
from modules.ai_modules.models.deepseek import DeepSeekModel
from workflows.my_workflows.entrypoint import OnDiscordMessageWorkflow
TOKENS_DIR = "tokens"


def is_tokens_set(app_name: str) -> bool:
    """Checks if a specific app's tokens are set."""
    file_path = os.path.join(TOKENS_DIR, f"{app_name}_tokens.json")
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return "access_token" in data
    except:
        return False


def setup_integrations_submenu():
    """Displays a sub-menu for 3rd party integrations."""
    while True:
        google_status = "SET" if is_tokens_set("google") else "NOT SET"
        print("\n====== 3rd Party Integrations Menu ======")
        print(f"1. Google Drive Integration [ {google_status} ]")
        print("2. Back to Main Menu")

        choice = input("Choose an option (1 or 2): ").strip()

        if choice == '1':
            # Run the Google OAuth flow
            run_google_oauth(
                scopes=["https://www.googleapis.com/auth/drive", 'https://www.googleapis.com/auth/calendar'], app_name="google"
            )
        elif choice == '2':
            # Return to the main menu
            break
        else:
            print("Invalid input. Please try again.")


def run_google_oauth(scopes: list, app_name: str) -> None:
    """
    Runs the Google OAuth2 flow and stores tokens for the specified app.

    Args:
        scopes (list): The scopes to request during the OAuth flow.
        app_name (str): The name of the app to associate with the tokens.
    """
    CLIENT_ID = os.getenv("GOOGLE_DRIVE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET")
    REDIRECT_URI = "http://localhost:8080"
    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    SCOPES = scopes

    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: CLIENT_ID or CLIENT_SECRET not set in environment.")
        return

    client = GoogleOAuthClient(
        CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_ENDPOINT, TOKEN_ENDPOINT, SCOPES
    )

    code_verifier, code_challenge = client.generate_pkce()
    auth_url = client.build_auth_url(code_challenge)

    client.start_callback_server()

    # Automatically open the authorization URL in the browser
    print("\nOpening the browser for authorization...")
    webbrowser.open(auth_url)
    print("\nWaiting for the authorization code...")
    while client.authorization_code is None:
        time.sleep(1)

    token_data = client.exchange_code_for_token(client.authorization_code, code_verifier)
    print("\n=== Token Response ===")
    print(token_data)

    # Dynamically assign tokens to the specified app name
    client.store_tokens(token_data, app_name=app_name)


def main():
    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Set 3rd party integrations")
        print("2. Activate workforce (start scheduled triggers)")
        print("3. Run test agent for functionality testing")
        print("4. Quit")

        choice = input("Enter your choice (1, 2, or 3): ").strip()

        if choice == '1':
            setup_integrations_submenu()
        elif choice == '2':
            print("Starting scheduled workflow system...")
            OnDiscordMessageWorkflow.execute(OnDiscordMessageWorkflow)
            # Assuming trigger is implemented
            print("Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping...")
        elif choice =='3':
            system_prompt = "You are an AI agent and will give me a mock json list of"
            # Now bring in our DeepSeekModel
            deepseek_model = DeepSeekModel(
                model_name="deepseek-chat",
                system_prompt=system_prompt,
                prompt_type="json"
            )

            agent = BaseAgent(
                model=deepseek_model,
                memory=None,
                tools=[]
            )


            result = agent.run("3 fictional patients and some mock data")
            print(result)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid menu selection. Please try again.")


if __name__ == "__main__":
    main()
