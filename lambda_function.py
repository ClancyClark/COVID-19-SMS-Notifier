from bs4 import BeautifulSoup
import requests
import time
import base64
import json
from urllib import request, parse

TWILIO_ACCOUNT_SID = 'YOUR_SID'
TWILIO_AUTH_TOKEN = 'YOUR_AUTH_TOKEN'
TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"

def send_sms(cases, deaths):
    to_number = 'YOUR_NUMBER'
    from_number = 'YOUR_TWILIO_NUMBER'
    body = f'North Carolina COVID-19 Update: Cases {cases}, Deaths {deaths}'

    if not TWILIO_ACCOUNT_SID:
        return "Unable to access Twilio Account SID."
    elif not TWILIO_AUTH_TOKEN:
        return "Unable to access Twilio Auth Token."
    elif not to_number:
        return "The function needs a 'To' number in the format +12023351493"
    elif not from_number:
        return "The function needs a 'From' number in the format +19732644156"
    elif not body:
        return "The function needs a 'Body' message to send."

    # insert Twilio Account SID into the REST API URL
    populated_url = TWILIO_SMS_URL.format(TWILIO_ACCOUNT_SID)
    post_params = {"To": to_number, "From": from_number, "Body": body}

    # encode the parameters for Python's urllib
    data = parse.urlencode(post_params).encode()
    req = request.Request(populated_url)

    # add authentication header to request based on Account SID + Auth Token
    authentication = "{}:{}".format(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    base64string = base64.b64encode(authentication.encode('utf-8'))
    req.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))

    try:
        # perform HTTP POST request
        with request.urlopen(req, data) as f:
            print("Twilio returned {}".format(str(f.read().decode('utf-8'))))
    except Exception as e:
        # something went wrong!
        return e

    return "SMS sent successfully!"
    
    
def current_covid_status():
    html = "https://www.ncdhhs.gov/covid-19-case-count-nc"
    page = requests.get(html)
    soup = BeautifulSoup(page.text, 'html.parser')
    table_rows = soup.find_all('td')
    # parse each
    # for row in table_rows:
    #     print(row)
    cases = table_rows[4].text.strip()
    deaths = table_rows[5].text.strip()
    print(f'Current Cases: {cases}')
    print(f'Current NC Deaths: {deaths}')
    
    report = f'North Carolina COVID-19 Update: NC Cases {cases}, NC Deaths {deaths}'
    print(report)
    result = send_sms(cases, deaths)
    return result


def lambda_handler(event, context):
    report = current_covid_status()
    return {
        'result': report
    }
