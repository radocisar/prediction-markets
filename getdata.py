import requests
import pandas as pd
import pprint as pp
import time
import json
from tqdm import tqdm
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

GAMMA_RATE = 500  # per 10 secs
CLOB_RATE = 9000  # per 10 secs


class RateLimiter:
    def __init__(self, rate, rate_window=10):
        self.rate = rate
        self.window = rate_window
        self.lock = threading.Lock()
        self.calls = deque()

    def acquire(self):
        while True:
            now = time.time()
            with self.lock():
                while self.calls and self.calls[0] <= now - self.rate_window:
                    self.calls.popleft()
                if len(self.calls) < self.rate:
                    self.calls.append(now)
                    return
            if wait:=(self.calls[0] + self.rate_window)-now) > 0:
                time.sleep(wait)

gamma_limiter = RateLimiter(GAMMA_RATE)
clob_limiter = RateLimiter(CLOB_RATE)

def fetch_clob(url):
    clob_limiter.acquire()
    resp = requests.get(f"https://clob.polymarket.com/book?token_id={clob_token}")
    return = resp.status_code, resp.json()

def fetch_gamma(url):
    gamma_limiter.acquire()
    resp = requests.get(f"https://gamma-api.polymarket.com/events?order=id&ascending=false&active=true&closed=false&limit={page_len}&offset={offset}")

    clob_urls = 

    with ThreadPoolExecutor(max_workers=500) as executor:
        fut = [executor.submit(fetch_clob, u) for u in clob_urls]
        for f in as_completed(fut):
            print(f.result())
    
    return


gamma_urls = # is there a way to get full {page_len}, so that all URLs can be built at the getgo?

with ThreadPoolExecutor(max_workers=500) as executor:
    fut = [executor.submit(fetch_gamma, u) for u in gamma_urls]
    for f in as_completed(fut):
        print(f.result())






status = requests.get("https://gamma-api.polymarket.com/status")
print(f"gamma API status: {status.status_code}")

page_len = 100
offset = 0
count = 0

# pbar = tqdm()

#######################
# All events
#######################
# while page_len == 100:
#     evts = requests.get(f"https://gamma-api.polymarket.com/events?order=id&ascending=false&active=true&closed=false&limit={page_len}&offset={offset}")
#     # print(evts.headers)
#     events = evts.json()

#     for evt in events:
#         count += 1
#
# time.sleep(0.02)
# page_len = len(events)
# offset += page_len
# pbar.update(page_len)
# # pbar.set_postfix(status="running")

# pbar.close()
# print(count)

#######################
# Latest event
#######################
evts = requests.get(
    f"https://gamma-api.polymarket.com/events?order=id&ascending=false&active=true&closed=false&limit=1&offset=0"
)
# pp.pprint(evts.json())
with open("events.json", "w") as f:
    json.dump(evts.json(), f, indent=2)

#######################
# Event by slug
#######################
evts = requests.get(
    f"https://gamma-api.polymarket.com/events?slug=fed-decision-in-march-885"
)
# pp.pprint(evts.json())
with open("fed.json", "w") as f:
    json.dump(evts.json(), f, indent=2)


# event = evts.json()[0]
# pp.pprint(json.dump(event))

# event_df = pd.DataFrame([event])
# print(event_df.head())
