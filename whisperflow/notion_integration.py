""" notion integration module """

from datetime import datetime
from notion_client import Client


def save_to_notion(
    api_key: str,
    database_id: str,
    transcription_text: str,
    duration_seconds: float,
    model: str,
) -> dict:
    """
    Save transcription to Notion database.

    Args:
        api_key: Notion API key
        database_id: Database ID to save to
        transcription_text: The transcribed text
        duration_seconds: Duration of recording in seconds
        model: Whisper model used

    Returns:
        dict with status and page_id or error message
    """
    try:
        client = Client(auth=api_key)

        # Create page in database
        response = client.pages.create(
            parent={"database_id": database_id},
            properties={
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": transcription_text[:100] or "Recording"
                            }
                        }
                    ]
                },
                "Transcription": {
                    "rich_text": [
                        {
                            "text": {
                                "content": transcription_text
                            }
                        }
                    ]
                },
                "Duration": {
                    "number": round(duration_seconds, 2)
                },
                "Model": {
                    "select": {
                        "name": model
                    }
                },
                "Timestamp": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                },
            },
        )

        return {
            "status": "success",
            "page_id": response["id"],
            "message": "Saved to Notion successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save to Notion: {str(e)}"
        }
