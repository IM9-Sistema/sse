from os import environ
import requests
from requests.exceptions import Timeout
from sys import exit

try:
	for i in range(8000, 8010):
		resp = requests.get(f"http://10.15.1.108:{i}/positions/subscribe", {"token": environ.get("SSE_USER_BYPASS_TOKEN", "")}, stream=True)
		assert resp.status_code == 200
		resp = requests.get(f"http://10.15.1.108:{i}/alerts/subscribe", {"token": environ.get("SSE_USER_BYPASS_TOKEN", "")}, stream=True)
		assert resp.status_code == 200
		exit(0)
except Exception as e:
	print(e)
	exit(1)