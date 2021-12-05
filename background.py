"""
from mib import create_app, create_celery

flask_app = create_app()
app = create_celery(flask_app)

try:
    import mib.tasks
except ImportError:
    raise RuntimeError('Cannot import celery tasks')
"""

from os import name
import os
import re
from celery import Celery
from celery.schedules import crontab

#from monolith.database import User, db, Message, Message_Recipient
#from mib.models import User

import datetime
from sqlalchemy.orm import aliased

#from monolith.emails import send_email
from mib.emails import send_email

import random


_APP = None
MIN_LOTTERY_POINTS = 1
MAX_LOTTERY_POINTS = 5

if os.environ.get('DOCKER_IN_USE') is not None:
    BACKEND = BROKER = 'redis://redis:6379'
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
        'schedule':  crontab() # crontab(0, 0, day_of_month='15') # frequency of execution: each 15 of the month
    },
}


@celery.task(name="lottery_notification")
def lottery_notification():
    global _APP
    # lazy init
    if _APP is None:
        #from monolith.app import create_app ----- REMOVE
        from mib import create_app
        
        os.environ["FLASK_ENV"] = "production"

        app = create_app()
        #from mib import db
        #db.init_app(app) # ----------------------- ??????
    else:
        app = _APP
    
    with app.app_context():
        from mib import db
        from mib.models import User
        #db.init_app(app) # ----------------------- ??????

        users = User.query.with_entities(User.id, User.email, User.firstname, User.lottery_points).all()
        for user in users: # users = [(id1, email1, firstname1, lottery_points1), (id2, email2, firstname2, lottery_points2), ...]
            
            recipient_id, recipient_email, recipient_firstname, recipient_lottery_points = user

            lottery_points = random.randint(MIN_LOTTERY_POINTS, MAX_LOTTERY_POINTS)

            message = f'Subject: Monthly lottery prize\n\nHi {recipient_firstname}! You won {lottery_points} points in the lottery.'
            send_email(recipient_email, message)

            recipient_lottery_points += lottery_points
            # Query to the db to update the total points of a user
            db.session.query(User).filter(User.id == recipient_id).update({'lottery_points': recipient_lottery_points})
            
        db.session.commit()

