import requests
import pandas as pd
import pprint as pp
import time
import json
from tqdm import tqdm
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

status = requests.get("https://clob.polymarket.com")
print(f"gamma API status: {status.status_code}")

status = requests.get("https://clob.polymarket.com")
print(f"CLOB API status: {status.status_code}")

GAMMA_RATE = 500  # per 10 secs
CLOB_RATE = 9000  # per 10 secs
GAMMA_PAGE_LEN = 10


class RateLimiter:
    def __init__(self, rate, rate_window=10):
        self.rate = rate
        self.rate_window = rate_window
        self.lock = threading.Lock()
        self.calls = deque()

    def acquire(self):
        while True:
            now = time.time()
            with self.lock:
                while self.calls and self.calls[0] <= now - self.rate_window:
                    self.calls.popleft()
                if len(self.calls) < self.rate:
                    self.calls.append(now)
                    return
            if (wait := (self.calls[0] + self.rate_window) - now) > 0:
                time.sleep(wait)


gamma_limiter = RateLimiter(GAMMA_RATE)
clob_limiter = RateLimiter(CLOB_RATE)


def fetch_clob(url):
    clob_limiter.acquire()
    # only get lowest ask on both "Y" and "N" sides
    resp = requests.get(url).json().get("asks", ["empty"])[-1]
    return resp.status_code, resp.json()


def fetch_gamma(url):
    start = time.time()
    gamma_limiter.acquire()
    events = requests.get(url)

    try:
        if evts := events.json():
            # print("-----------------------------------------------------")
            # pp.pprint(evts)
            # print("-----------------------------------------------------")
            # only if there are events returned
            clob_urls = [
                f"https://clob.polymarket.com/book?token_id={clob_token}"
                for event in evts
                for market in event["markets"]
                if market["active"]
                for clob_token in json.loads(market["clobTokenIds"])
            ]
            #     fut = [executor.submit(fetch_clob, u) for u in clob_urls]
            #     for f in as_completed(fut):
            #         print(f.result())

        return f"lenght: {len(clob_urls)}, start_time: {start}, end_time: {time.time()}, duration: {time.time() - start}, thread: {threading.current_thread().name}"
    except Exception as e:
        raise Exception(
            f"Error fetching gamma data: {e}, url: {url}"
            # f"Error fetching gamma data: {e}, url: {url}, events: {[market["slug"] for e in events.json() for market in e["markets"]]}"
        )


gamma_urls = [
    f"https://gamma-api.polymarket.com/events?order=id&ascending=false&active=true&closed=false&limit={GAMMA_PAGE_LEN}&offset={offset}"
    for offset in range(0, 10000, GAMMA_PAGE_LEN)
]

with ThreadPoolExecutor(max_workers=20) as executor:
    fut = [executor.submit(fetch_gamma, u) for u in gamma_urls]
    for f in as_completed(fut):
        print(f.result())

# pbar = tqdm()
