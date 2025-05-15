from api import interface

import imaplib
import email
from email.header import decode_header

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import dotenv_values


# Gmail IMAP settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

# Gmail SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


class gmailAPI(interface.MailAPI):
    def __init__(self):
        """imap setup"""
        # load config
        config = dotenv_values(".env")

        # Connect to Gmail IMAP
        imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        imap.login(config["email"], config["email_psswd"])

        # Select the inbox
        imap.select("inbox")

        self.imap = imap

        """smtp setup"""
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(config["email"], config["email_psswd"])

        self.smtp = server

        """set vars"""
        self.email = config["email"]



    def fetch(self) -> tuple:
        # Search for unread emails
        status, messages = self.imap.search(None, "ALL")

        email_list = []

        if messages[0]:
            email_ids = messages[0].split()
            for email_id in email_ids:
                # Fetch email
                status, msg_data = self.imap.fetch(email_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        # Parse email
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decode subject
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8")

                        # Decode sender
                        sender, encoding = decode_header(msg.get("From"))[0]
                        if isinstance(sender, bytes):
                            sender = sender.decode(encoding or "utf-8")

                        # Extract email body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type == "text/plain":
                                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                        # Store email data
                        email_list.append({"subject": subject, "sender": sender, "content": body})

        return email_list


    def send(self, to: str, subject: str, content: str):
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(content, "plain"))

        # Send email
        self.smtp.sendmail(self.email, to, msg.as_string())
        print("Email sent successfully!")

    def __del__(self):
        self.imap.logout()
        self.smtp.quit()
