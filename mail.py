from sendgrid import *
from sendgrid.helpers.mail import *
from dotenv import load_dotenv
import os

sg = SendGridAPIClient(api_key='') 
from_email = Email("devmonty2002@gmail.com")
to_email = Email("devmonty2002@gamil.com")
subject = "mail sent"
content = Content( "text/plain", "checking" )
mail = Mail(from_email, subject, to_email, content)
response = sg.client.mail.send.post(request_body=mail.get())

print(response.status_code)
print(response.body)
print(response.headers)