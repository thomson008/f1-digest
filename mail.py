import smtplib
from email.message import EmailMessage
from race import get_next_race, get_last_results_and_standings
from datetime import datetime
import imaplib
import email
from replit import db

def send_email(subject, body, to, login_info):
    """
    Sends email with a given subject and body to a specified recipient
    """
    ADDRESS, PASSWORD = login_info

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"F1 Digest <{ADDRESS}>"
    msg['To'] = to

    msg.set_content(body)

    print(f'Sending email to {to}, time: {datetime.now()}')
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(ADDRESS, PASSWORD)
        smtp.send_message(msg)


def generate_email(mail, env):
    """
    Generates subject and body of the email to be sent.
    Fetches the list of subscribers and sends to all of them.
    """
    race, results, standings = get_last_results_and_standings()
    next_race = get_next_race()

    subject = f"Race digest - F1 2021 | Round {race.round} | {race.name}"
    body = (f"Results:\n{results}\n\nCurrent standings:\n"
        f"{standings}\n\nNext race: {next_race}")

    login_info = env['EMAIL_ADDRESS'], env['EMAIL_PASSWORD']

    subs = update_db_and_get_subs(mail, (env['EMAIL_ADDRESS'], env['EMAIL_PASSWORD']))

    for sub in subs:
        send_email(subject, body, sub, login_info)


def check_for_subscribers(mail, login_info):
    """
    Downloads a list of subscribers by inspecting the senders of current messages
    in the mailbox.
    """
    ADDRESS, PASSWORD = login_info

    try:
        mail.select('inbox')
        data = mail.search(None, 'ALL') 
    except:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(ADDRESS, PASSWORD)
        mail.select('inbox')
        data = mail.search(None, 'ALL')
        
    mail_ids = data[1]
    id_list = mail_ids[0].split()   

    if not id_list:
        return []

    first_email_id = int(id_list[0])
    latest_email_id = int(id_list[-1])

    subscribers = []

    for i in range(latest_email_id, first_email_id-1, -1):
        data = mail.fetch(str(i), '(RFC822)')
        for response_part in data:
            arr = response_part[0]
            if isinstance(arr, tuple):
                msg = email.message_from_string(str(arr[1],'utf-8'))
                email_from = msg['from']
                subscribers.append(email_from)

    return subscribers


subscribe_body = """
You have succesfully subscribed to F1 Digest.

You will now receive a race summary email in the evening after every Grand Prix.
This summary will include the results and current standings.

You will also get a reminder of the time, date and place of the next GP!

All the best,
F1 Digest
"""

def update_db_and_get_subs(mail, login_info):
    """
    Checks if any new subsribers have appeared in the mailbox 
    and if so, adds them to the database.

    Returns the updated list of subscribers
    """
    subscribers = check_for_subscribers(mail, login_info)

    db_subs = []
    if 'subscribers' in db.keys():
        db_subs = db['subscribers']

    for sub in subscribers:
        if sub not in db_subs:
            print(f'New subscriber added: {sub}')
            db_subs.append(sub)
            subject = "Welcome to F1 Digest!"
            send_email(subject, subscribe_body, sub, login_info)

    db['subscribers'] = db_subs

    return db_subs