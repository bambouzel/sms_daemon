import sys

class DummyModem:
    def __init__(self, logger, port, baud, timeout=5):
        self.port=port
        self.baud=baud
        self.logger=logger
        self.timeout=timeout
        self.portstr='{}:{}'.format(port, baud)

    def close(self):
        self.logger.info("modem closed")
        return

    def write(self, data):
        self.logger.info('modem: {}'.format(data.decode("utf-8")))
        self.request=data.decode("utf-8")
        return

    def read(self, size):
        if ("AT+CPIN?" in self.request):
            answer="READY"
        elif ("AT+CMGS=" in self.request):
            answer = ">"
        elif ("AT+CMGL=\"ALL\"" in self.request):
            answer='+CMGL: 1,"REC READ","1984","","19/01/18,15:51:54+04"\r\nHey Viking. Welkom bij Mobile Vikings! Proficiat: je simkaart is nu 100% actief. Vragen of opmerkingen? Je weet ons te vinden.'
            answer=answer + '\r\n+CMGL: 2,"REC READ","1984","","19/02/16,16:01:59+04"\r\nMobile Vikings info: je bundel met gratis data en sms\'en, en je Vikingvoordeel vervalt op 18/02/2019 om 15:51:33. Herlaad op tijd voor een nieuwe bundel!'
            answer=answer + '\r\n+CMGL: 3,"REC READ","1984","","19/02/17,21:27:39+04"\r\nen herladen dan.'
            answer=answer + '\r\n+CMGL: 4,"REC READ","1984","","19/02/18,16:02:27+04"\r\nMobile Vikings info: je gratis bundel is vervallen. Bellen, surfen en sms\'en doe je nu met je belwaarde. Wil je je gratis bundel vernieuwen? Even herladen dan.'
            answer=answer + '\r\n+CMGL: 5,"REC READ","1984","","19/02/17,21:27:39+04"\r\nMobile Vikings info: je gratis bundel vervalt op 18/02/2019 om 15:51. Daarna bel, sms en surf je met je belwaarde. Wil je je gratis bundel vernieuwen? Ev'
            answer=answer + '\r\nOK'
        elif ("AT+CMGR=2" in self.request):
            answer='+CMGR: "REC READ","1984","","19/02/16,16:01:59+04"\r\nMobile Vikings info: je bundel met gratis data en sms\'en, en je Vikingvoordeel vervalt op 18/02/2019 om 15:51:33. Herlaad op tijd voor een nieuwe bundel!'
            answer=answer + '\r\nOK'
        else:
            answer="OK"
        return answer.encode()
