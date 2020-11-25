from datetime import datetime, timedelta
from api_gateway.classes.user import User
import requests, os
from collections import namedtuple

FilterUser = namedtuple("FilterUser", ["email", "phone", "fiscal_code"])

INCUBATION_PERIOD_COVID = 14

def mark_user(user_id: int):
    """ Mark a user as positive.
    Args:
        userid (int): Id of the customer
    Returns:
        str: '' in case of success, a error message string in case of failure.
    """
    user = User.get(id=user_id)
    user_dict = None
    if user == None:
        message = 'Error! Unable to mark the user. User not found'
    elif user.is_positive == False:
        user.is_positive = True
        user.reported_positive_date = datetime.now()
        user.submit()
        message = ''
        
        requests.get(f"http://{os.environ.get('GOS_NOTIFICATION')}/notifications/contact_tracing​​​/{user_id}")
    else:
        message = 'You\'ve already marked this user as positive!'

    return message, user

def search_user(filter_user: FilterUser):
    if filter_user.email == '' and filter_user.fiscal_code == '' and filter_user.phone == '':
        return None, 'At least one in fiscal code, email or phone number is required'

    if filter_user.phone != None and filter_user.phone != '' and len(filter_user.phone) < 9:
        return None, 'Invalid phone number'

    if filter_user.fiscal_code != None and filter_user.fiscal_code != '' and len(filter_user.fiscal_code) != 16:
        return None, 'Invalid fiscal code'
    

    #if filter_user.firstname != "":
    #    q = q.filter(func.lower(User.firstname) == func.lower(filter_user.firstname))
    #if filter_user.lastname != "":
    #    q = q.filter(func.lower(User.lastname) == func.lower(filter_user.lastname))
    if filter_user.email != None and filter_user.email != '':
        user = User.get(email=filter_user.email)
    if filter_user.phone != None and filter_user.phone != '':
        user = User.get(phone=filter_user.phone)
    if filter_user.fiscal_code != None and filter_user.fiscal_code != '':
        user = User.get(fiscal_code=filter_user.fiscal_code)

    if user == None:
        return None, 'No user found'
    else:
        return user, 'OK'