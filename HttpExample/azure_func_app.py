from twilio.rest import Client
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.calendar.calendar_view.calendar_view_request_builder import CalendarViewRequestBuilder
from dotenv import load_dotenv

import azure.functions as func
import logging
import os
import json
import datetime
import pytz
import asyncio

logging.basicConfig(level=logging.INFO)
load_dotenv()

def convert_to_pst(date_time_str):
    utc_timezone = pytz.timezone("UTC")
    dt = datetime.datetime.fromisoformat(date_time_str)
    dt_utc = utc_timezone.localize(dt)
    pst_timezone = pytz.timezone('America/Los_Angeles')
    dt_pst = dt_utc.astimezone(pst_timezone)
    return dt_pst

async def fetch_calendar_view(graph_client, user_id, request_config):
    calendar_view = await graph_client.users.by_user_id(user_id).calendar.calendar_view.get(request_configuration=request_config)
    logging.info(f"Calendar view value: {calendar_view}")
    return calendar_view

def main(myTimer: func.TimerRequest) -> func.HttpResponse:
    logging.info('Python Timer trigger function processed a request.')

    try:
        # Get Twilio credentials from app settings (environment variables)
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        from_number = os.environ["TWILIO_PHONE_NUMBER"]
        recipient_number = os.environ["RECIPIENT_PHONE_NUMBER"]

        # Get the client ID and secret from environment variables
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        user_id = os.getenv('USER_ID')

        # Verify that environment variables are set before proceeding
        if not all([account_sid, auth_token, from_number, recipient_number, client_id, client_secret, tenant_id, user_id]):
            raise ValueError("One or more required environment variables are not set. Please check your .env file.")
        logging.info("Environment variables initialized successfully")
        logging.info(f"Recipient number: {recipient_number}")
        logging.info(f"User ID: {user_id}")
        
        # Create Azure Client Secret Credential
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        logging.info("Azure Client Secret Credential initialized successfully")

        # Create a Graph client using the credential object
        graph_client = GraphServiceClient(credential)
        logging.info("Graph client initialized successfully")

        # Create datetime objects for the date range
        now = datetime.datetime.now(pytz.timezone("America/Los_Angeles"))
        start_date = now
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        logging.info(f"start_date: {start_date}")
        logging.info(f"end_date: {end_date}")

        # Create query parameters for the calendar view request
        query_parameters = CalendarViewRequestBuilder.CalendarViewRequestBuilderGetQueryParameters(
            start_date_time=start_date,
            end_date_time=end_date,
            top=10,
            select=['subject', 'organizer', 'start', 'end', 'isAllDay', 'location', 'bodyPreview', 'importance'],
            orderby=['start/dateTime asc']
        )
        logging.info(f"query_parameters: {query_parameters}")
        logging.info(f"Fetching calendar events for user {user_id} from {start_date} to {end_date}")

        # Retrive Calendar View for specific user for the current datetime until midnight
        # Step 1: Create request parameters
        request_config = CalendarViewRequestBuilder.CalendarViewRequestBuilderGetRequestConfiguration(
            query_parameters=query_parameters
        )
        logging.info(f"request_config: {request_config}")

        # Step 2: Make the call
        calendar_view = asyncio.run(fetch_calendar_view(graph_client, user_id, request_config))

        # Step 3: Process and display the events
        parts = []
        parts.append("<Response>")
        parts.append("""<Pause length="1"/>""")
        todaysDate = now.strftime("%a %b %d")
        parts.append(f"<Say>Hello Ramon!, this is MK. Here are your events for {todaysDate}.</Say>")
       
        if hasattr(calendar_view, 'value') and calendar_view.value:
            parts.append("""<Pause length="1"/>""")
            parts.append(f"<Say>You have {len(calendar_view.value)} calendar event(s).</Say>")
            
            for i, event in enumerate(calendar_view.value, 1):
                # Extract and format event details
                subject = event.subject or "(No subject)"
                organizer = event.organizer.email_address.name if event.organizer and hasattr(event.organizer, 'email_address') else "Unknown"
            
                start_time_dt_pst = convert_to_pst(event.start.date_time)
                start_time = start_time_dt_pst.strftime("%-I:%M %p")

                end_time_dt_pst = convert_to_pst(event.end.date_time)
                end_time = end_time_dt_pst.strftime("%-I:%M %p %Z")

                location = event.location.display_name if event.location.display_name else "No location"
                
                # Create a Twilio message part for each event
                parts.append("""<Pause length="1"/>""")
                parts.append(f"<Say>Event {i}: {subject} </Say>")
                parts.append(f"<Say>from {start_time} to {end_time}</Say>")
                parts.append(f"<Say>located at {location}</Say>")
                parts.append(f"<Say>organized by {organizer}</Say>")
                if event.is_all_day:
                    parts.append("""<Pause length="1"/>""")
                    parts.append(f"<Say>This is an all day event</Say>")
                if event.importance and event.importance != 'normal':
                    parts.append("""<Pause length="1"/>""")
                    parts.append(f"<Say>Importance: {event.importance}</Say>")
        else:
            parts.append("""<Pause length="1"/>""")
            parts.append("<Say>No events found in the specified time range.</Say>")

        parts.append("""<Pause length="1"/>""")
        parts.append("<Say>Thank you for using MK your friendly AI Agent.</Say>")    
        parts.append("</Response>")
        logging.info(f"parts: {json.dumps(parts, indent=2)}")

        # Create Twilio client
        client = Client(account_sid, auth_token)

        # Make the call
        call = client.calls.create(
            twiml="".join(parts),
            to=recipient_number,
            from_=from_number,
        )

        return func.HttpResponse(
            json.dumps({"success": True, "call_sid": call.sid}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error making call: {str(e)}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )