from os import environ
import requests
from requests.exceptions import Timeout

if __name__ == "__main__":
	try:
		requests.get("http://127.0.0.1:8000", {"token", environ.get("SSE_USER_BYPASS_TOKEN", "")}, stream=True)
		exit(0)
	except:
		exit(1)