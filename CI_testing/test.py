#!/usr/bin/env python3

import requests
import time

time.sleep(15)
try:
    r = requests.get("http://localhost:8000")
    r.raise_for_status()
    print(r.status_code)
    if r.status_code != 200:
        exit(1)
except requests.exceptions.HTTPError as err:
    print(err)
    exit(20)

except:
    print("general error")
    exit(1)

print("Succeeded")
exit(0)
