import azure.functions as func
import logging
import os
import json
from twilio.rest import Client

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get Twilio credentials from app settings (environment variables)
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        from_number = os.environ["TWILIO_PHONE_NUMBER"]
        recipient_number = os.environ["RECIPIENT_PHONE_NUMBER"]

        if not recipient_number:
            return func.HttpResponse(
                "Please provide a recipient phone number in the request body or set RECIPIENT_PHONE_NUMBER in app settings.",
                status_code=400,
            )

        # Create Twilio client
        client = Client(account_sid, auth_token)

        # Make the call
        call = client.calls.create(
            twiml="""<Response>
                <Pause length="1"/>
                <Say>Hi Aldred -- this is Jairosoft AI.</Say> 
                <Pause length="1"/>
                <Say>I've got your schedule for Sunday, April 20th, 2025:</Say>
                <Pause length="1"/>
                <Say>8:00 AM - 9:00 AM: Meeting with Miles</Say>
                <Pause length="1"/>
                <Say>9:00 AM - 10:00 AM: Meeting with Jayden</Say>
                <Pause length="1"/>
                <Say>11:00 AM - 12:00 PM: Lunch with Family</Say>
                <Pause length="1"/>
                <Say>1:00 PM - 5:00 PM: Meeting with Kriss</Say>
                <Pause length="1"/>
                <Say>Looks like a busy day!</Say>
                <Pause length="1"/>
                <Say>Is there anything else I can help you with regarding this schedule?</Say>
            </Response>""",
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