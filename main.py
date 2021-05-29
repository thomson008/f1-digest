import os
from threading import Timer
from datetime import datetime
from race import get_all_races, get_ymd
from mail import generate_email, update_db_and_get_subs
from keep_alive import keep_alive
import imaplib
import time

def create_email_schedule_threads(func, mail):
    """
    Creates individual delayed threads for each race, 
    in order to send emails in the evening of every race day. 
    """
    now = datetime.now()
    races = get_all_races()

    timers = []
    for race in races:
        year, month, day = get_ymd(race.date)
        run_at = datetime(year, month, day, 19)

        delay = (run_at - now).total_seconds()

        if delay >= 0:
            timer = Timer(delay, func, [os.environ, mail])
            timers.append(timer)

    return timers


# Create a mail object and authenticate
mail = imaplib.IMAP4_SSL('imap.gmail.com')
ADDRESS, PASSWORD = os.environ['EMAIL_ADDRESS'], os.environ['EMAIL_PASSWORD']
mail.login(ADDRESS, PASSWORD)

# Check if there are any subscriptions in the mailbox
update_db_and_get_subs(mail, (ADDRESS, PASSWORD))

# Create delayed threads for every race
threads = create_email_schedule_threads(generate_email, mail)

# Start all the threads
for thread in threads:
	thread.start()

keep_alive()

# Start infinite checking for new subscribers
while True:
    update_db_and_get_subs(mail, (ADDRESS, PASSWORD))
    time.sleep(60)