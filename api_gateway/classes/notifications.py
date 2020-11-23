from api_gateway.classes.utils import safe_get
import requests
import os, logging


def fetch_notifications(user, unread_only=False):
    # customer case
    if user.restaurant_id is None:
        try:
            resp = safe_get(f"http://{os.environ.get('GOS_NOTIFICATION')}/notifications/user/{user.id}?unread_only={unread_only}")
            return resp.json()['notifications']
        except Exception as e:
            logging.error(e)
            # in case notification service is down, report no notification to the user
            return []
    else:
        try:
            resp = safe_get(f"http://{os.environ.get('GOS_NOTIFICATION')}/notifications/restaurant/{user.id}?unread_only={unread_only}")
            return resp.json()['notifications']
        except Exception as e:
            logging.error(e)
            return []

def get_notification_by_id(notification_id):
    try:
        resp = safe_get(f"http://{os.environ.get('GOS_NOTIFICATION')}/notifications/{notification_id}")
        return resp.json()['notifications']
    except Exception as e:
        logging.error(e)
        # in case notification service is down, report no notification to the user
        return {}