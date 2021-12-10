from logging import Manager
from os import name
import os
import re
from celery import Celery
from celery.schedules import crontab

import datetime
from sqlalchemy.orm import aliased

from mib.emails import send_email

import random


_APP = None
MIN_LOTTERY_POINTS = 1
MAX_LOTTERY_POINTS = 5

if os.environ.get('DOCKER_IN_USE') is not None:
    BACKEND = BROKER = 'redis://redis_users:6379'
else:
    BACKEND = BROKER = 'redis://localhost:6379'

celery = Celery(__name__, backend=BACKEND, broker=BROKER) 


celery.conf.timezone = 'Europe/Rome' # set timezone to Rome

# 
# 1st task: definition of a periodic task that checks if the lottery needs to be performed.
# for simplicity, the lottery is performed on the 15th of every month for each users, independently from the registration date
# 
celery.conf.beat_schedule = {
    'lottery_notification': {
        'task': 'lottery_notification', 
        'schedule': crontab(0, 0, day_of_month='15') # frequency of execution: each 15 of the month
    },
}



@celery.task(name="lottery_notification")
def lottery_notification():
    global _APP
    # lazy init
    if _APP is None:
        from mib import create_app
        app = create_app()
        _APP = app
    else:
        app = _APP
    
    with app.app_context():
        from mib.dao.user_manager import UserManager
        from mib.models.user import User

        users = UserManager.retrieve_all_users()
        
        for user in users:
            
            recipient_id = user.id
            recipient_email = user.email
            recipient_firstname = user.firstname
            
            lottery_points = random.randint(MIN_LOTTERY_POINTS, MAX_LOTTERY_POINTS)

            message = f'Subject: Monthly lottery prize\n\nHi {recipient_firstname}! You won {lottery_points} points in the lottery.'
            send_email(recipient_email, message)

            # Query to the db to update the total points of a user
            user.lottery_points += lottery_points
            UserManager.update_user(user)

        print("FINITO DI AGGIUNGERE PUNTI")

        return True
        