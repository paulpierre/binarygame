# credentials
import smtplib,sys,os,traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Lets define the pretty colors for the command line
class colors:
    green = '\033[1;32;40m'
    red = '\033[1;31;40m'
    reset = '\033[0m'
    grey = '\033[1;30;40m'
    white = '\033[1;39;40m'

class Gmail:

    gmail_user = None
    gmail_password = None

    mail_from = None
    mail_to = None
    mail_from_name = None
    mail_body = None
    mail_subject = None

    # -----------
    # Initialize
    # -----------
    def __init__(self, gmail_user=False, gmail_password=False):
        print('gmail: ' + gmail_user)

        self.gmail_user = gmail_user
        self.gmail_password = gmail_password

        if not gmail_user or not gmail_password:
            raise Exception('Gmail credentials for mailer bot not provided')


    def send(self):

        if not self.mail_body:
            raise Exception('Must specify a message to send')

        if not self.mail_from_name:
            self.mail_from_name = 'Crush or Crater Bot'

        self.mail_from = str(self.mail_from_name) + ' <' + str(self.mail_from) + '>'

        if not self.mail_to:
            self.mail_to = 'guitarsmith@gmail.com'

        if not self.mail_subject:
            self.mail_subject = str(self.mail_from_name) + ' Report: ' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.mail_subject
        msg['To'] = self.mail_to
        msg['From'] = self.mail_from

        html = '<html><head></head><body>' + self.mail_body + '</body>'
        msg.attach(MIMEText(html, 'html'))

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.gmail_user, self.gmail_password)
            server.sendmail(self.mail_from, self.mail_to.split(","), msg.as_string())
            server.close()

            print(colors.green + 'DONE! ' + colors.reset + 'Email sent!')

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            print(traceback.format_exc())
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit(0)