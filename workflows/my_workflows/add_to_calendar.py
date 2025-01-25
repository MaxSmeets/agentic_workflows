# workflows/my_workflows/add_to_calendar.py
import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from workflows.base_workflow import Workflow

class AddToCalendarWorkflow(Workflow):
    def execute(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        location: str = "",
        description: str = "",
        calendar_id: str = "primary"
    ) -> str:
        """
        Creates an event in the specified Google Calendar using previously authorized OAuth tokens.
        :param summary: Title of the event.
        :param start_time: Start date/time in RFC3339 (e.g. "2025-02-01T10:00:00-07:00")
        :param end_time: End date/time in RFC3339.
        :param location: (Optional) Event location.
        :param description: (Optional) Event description.
        :param calendar_id: (Optional) Calendar ID, defaults to "primary".
        :return: A string message about the created event or any errors.
        """

        # 1. Load stored tokens from your OAuth flow
        token_path = os.path.join("tokens", "google_tokens.json")
        if not os.path.exists(token_path):
            return "No OAuth tokens found. Please authorize Google first."

        with open(token_path, "r") as f:
            token_data = json.load(f)

        # 2. Build Credentials object from these tokens
        creds = Credentials(
            token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_DRIVE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_DRIVE_CLIENT_SECRET"),
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        # 3. Refresh token if necessary (the google-auth library handles the logic)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Optionally store updated credentials back to file
            updated_token_data = {
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "scope": " ".join(creds.scopes),
                "token_type": "Bearer"
            }
            with open(token_path, "w") as f:
                json.dump(updated_token_data, f, indent=2)

        # 4. Build the Google Calendar service
        service = build("calendar", "v3", credentials=creds)

        # 5. Construct the event body
        event_body = {
            "summary": summary,
            "start": {
                "dateTime": start_time,
                "timeZone": "America/Los_Angeles"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "America/Los_Angeles"
            },
        }

        # Add optional fields if they are provided
        if location:
            event_body["location"] = location
        if description:
            event_body["description"] = description

        try:
            event = service.events().insert(
                calendarId=calendar_id, body=event_body
            ).execute()
            return f"Event created successfully! View it here: {event.get('htmlLink')}"
        except Exception as e:
            return f"Failed to create event: {str(e)}"
