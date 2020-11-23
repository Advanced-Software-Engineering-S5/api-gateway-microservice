import requests
import logging
from requests.exceptions import Timeout
from api_gateway.classes.exceptions import TimeoutError

TIMEOUT_SECS = 1 
RETRIES = 2
def safe_get(url: str, retries=RETRIES):
    if retries == 0:
        raise TimeoutError
    try:
        requests.get(url, timeout=TIMEOUT_SECS)
    except Timeout as e:
        safe_get(url, retries-1)

def safe_post(url: str, json: dict, retries=RETRIES):
    if retries == 0:
        raise TimeoutError
    try:
        requests.post(url, json=json, timeout=TIMEOUT_SECS)
    except Timeout as e:
        safe_post(url, retries-1)


def safe_put(url: str, json: dict, retries=RETRIES):
    if retries == 0:
        raise TimeoutError
    try:
        requests.put(url, json=json, timeout=TIMEOUT_SECS)
    except Timeout as e:
        safe_put(url, retries-1)

def safe_delete(url: str, retries=RETRIES):
    if retries == 0:
        raise TimeoutError
    try:
        requests.delete(url, timeout=TIMEOUT_SECS)
    except Timeout as e:
        safe_delete(url, retries-1)