from bs4 import BeautifulSoup
import requests
import time
import base64
import json
from urllib import request, parse

TWILIO_ACCOUNT_SID = 'YOUR_SID'
TWILIO_AUTH_TOKEN = 'YOUR_AUTH_TOKEN'
TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
TARGET_TO_PHONE_NUMBERS = ['+1-ADD NUMBER','+1-ADD NUMBER']


def send_sms(the_message, to_phone_number):
    to_number = to_phone_number
    from_number = '+13367702882'
    body = the_message

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
            print('made it here')
            print("Twilio returned {}".format(str(f.read().decode('utf-8'))))
    except Exception as e:
        # something went wrong!
        return e
    return 'Successful SMS!'
    
    

def current_covid_status():
    html = "https://www.ncdhhs.gov/covid-19-case-count-nc"
    page = requests.get(html)
    soup = BeautifulSoup(page.text, 'html.parser')
    rows = soup.find_all('td')
    # # parse each
    # for row in rows:
    #     print(row)
    cases = rows[0].text.strip().replace(',','')
    deaths = rows[1].text.strip().replace(',','')
    total_tested = rows[2].text.strip().replace(',','')
    in_hosp = rows[3].text.strip().replace(',','')
    percent_positive = (int(cases)/int(total_tested))*100
    current_mortality = (int(deaths)/int(cases))*100
    percent_hospitalized = (int(in_hosp)/int(cases))*100
    print(f'Current NC Cases: {cases}')
    print(f'Current NC Deaths: {deaths}')
    print(f'Current NC in Hospital: {in_hosp}')
    print(f'Current NC Mortality: {current_mortality:.1f}%')
    print(f'Hospitalized: {in_hosp} ({percent_hospitalized:.1f}%)')
    sms_message = f'COVID-19 Update--NC Cases:{cases} NC Deaths: {deaths}'\
             f' In NC, {percent_positive:.1f}% tested were positive.'\
             f' {current_mortality:.1f}% risk of death.'\
             f' Hospitalized: {in_hosp} ({percent_hospitalized:.1f}%)'
    print(sms_message)
    for number in TARGET_TO_PHONE_NUMBERS:
        send_sms(sms_message, number)
        time.sleep(1)
    print('sms loop done.')
    return 'process complete!'


def lambda_handler(event, context):
    report = current_covid_status()
    return {
        'result': report
    }
