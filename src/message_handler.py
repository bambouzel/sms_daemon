from requests import get
from requests import post
import subprocess
import json
import time

# https://developers.home-assistant.io/docs/en/external_api_rest.html

#
# constants in module
#
URL_STATES = "http://192.168.1.38:8123/api/states"
URL_SERVICES = "http://192.168.1.38:8123/api/services"
BEARER = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI4YTNkZDllNjIzM2E0YTU3YjNlOGNlNzc0OTZmZmE1NCIsImlhdCI6MTU3MDI5Mzk5MSwiZXhwIjoxODg1NjUzOTkxfQ.r7NSM-mCnOmsBS3WHO90DIBi2JCyAJuggC5zTP2a2hg"
HEADERS = {
    'Authorization': 'Bearer ' + BEARER,
    'content-type': 'application/json',
}
JSON = {
    'entity_id': 'alarm_control_panel.home_alarm'
}
class MessageHandler:
    def __init__(self, logger):
        self.logger=logger

    def handle(self, sms, recipient, message):
        self.logger.info('recipient: {} message: {}'.format(recipient, message))
        if ('ping' == message):
            sms.sendSMS(recipient, 'pong')
        elif ('status' == message):
            sms.sendSMS(recipient, self.status())
        elif ('disarm' == message):
            sms.sendSMS(recipient, self.disarm())
        elif ('arm' == message):
            sms.sendSMS(recipient, self.arm())
        elif ('report' == message):
            sms.sendSMS(recipient, self.report())

    def status(self):
        response = get(URL_STATES + '/alarm_control_panel.home_alarm', headers=HEADERS)
        data = json.loads(response.text)
        return data['state']

    def arm(self):
        post(URL_SERVICES + '/alarm_control_panel/alarm_arm_home', headers=HEADERS, json=JSON)
        return 'ok'

    def disarm(self):
        post(URL_SERVICES + '/alarm_control_panel/alarm_disarm', headers=HEADERS, json=JSON)
        return 'ok'

    def report(self):
        response = get(URL_STATES, headers=HEADERS)
        states = json.loads(response.text)
        result = ''
        for state in states:
            if ((state['entity_id'].find('contact') > 0) or (state['entity_id'].find('occupancy') > 0)):
                result = result + '{} -> {} (link: {}, battery: {})\n'.format(state['attributes']['friendly_name'], state['state'], state['attributes']['linkquality'], state['attributes']['battery'])
        return result
