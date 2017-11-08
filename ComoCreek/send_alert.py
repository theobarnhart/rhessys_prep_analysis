import sys
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

subject = sys.argv[1] # pull out the argument from the commend line
message = sys.argv[2] 

server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
server.login('barnhatb@colorado.edu', "jxfwbdloxrdtuxpg")

msg = MIMEMultipart()
msg['From'] = 'barnhatb@colorado.edu'
msg['To'] = 'barnhatb@colorado.edu'
msg['Subject'] = subject

msg.attach(MIMEText(message,'plain'))

server.sendmail("barnhatb@colorado.edu", "barnhatb@colorado.edu", msg.as_string())
server.quit()
