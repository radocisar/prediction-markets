import requests
import pandas as pd
import pprint as pp
import time
import json
from tqdm import tqdm
import threading
from queue import Queue
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed


status = requests.get("https://clob.polymarket.com")
print(f"gamma API status: {status.status_code}")

status = requests.get("https://clob.polymarket.com")
print(f"CLOB API status: {status.status_code}")

GAMMA_RATE = 500  # per 10 secs
CLOB_RATE = 4500  # per 10 secs
GAMMA_PAGE_LEN = 100


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


def writer(q):
    with open("clob_prices_3.csv", "w") as f:
        while True:
            if (msg := q.get()) is not None:
                f.write(msg + "\n")


q = Queue()
threading.Thread(target=writer, args=(q,), daemon=True).start()

gamma_limiter = RateLimiter(GAMMA_RATE)
clob_limiter = RateLimiter(CLOB_RATE)


def fetch_clob(m):
    clob_limiter.acquire()
    # only get lowest ask on both "Y" and "N" sides
    # print("reached clob")
    # print(m["clobTokenIds"])

    clob_tokens = json.loads(m["clobTokenIds"])
    y_resp = requests.get(f"https://clob.polymarket.com/book?token_id={clob_tokens[0]}")
    n_resp = requests.get(f"https://clob.polymarket.com/book?token_id={clob_tokens[1]}")

    if y_resp and n_resp:
        y_ask_price = y_resp.json().get("asks", [{}])[-1].get("price", None)
        n_ask_price = n_resp.json().get("asks", [{}])[-1].get("price", None)
        y_ask_size = y_resp.json().get("asks", [{}])[-1].get("size", None)
        n_ask_size = n_resp.json().get("asks", [{}])[-1].get("size", None)
        # print(f"Y Ask: {y_ask_price}, N Ask: {n_ask_price}")
        if y_ask_price and n_ask_price:
            total = float(y_ask_price) + float(n_ask_price)
            # print(total)
            q.put(
                f'"{m["mkt_question"]}", {m["mkt_slug"]}, {str(total)}, {str(y_ask_price)}, {str(y_ask_size)}, {str(n_ask_price)}, {str(n_ask_size)}'
            )
            if total < 1.0:
                print(
                    f"mkt_question: {m['mkt_question']}, mkt_slug: {m['mkt_slug']}, total: {total}, y_ask_price: {y_ask_price}, y_ask_size: {y_ask_size}, n_ask_price: {n_ask_price}, n_ask_size: {n_ask_size}"
                )
            return f"mkt_question: {m['mkt_question']}, mkt_slug: {m['mkt_slug']}, total: {total}, y_ask_price: {y_ask_price}, y_ask_size: {y_ask_size}, n_ask_price: {n_ask_price}, n_ask_size: {n_ask_size}"
        # return f"resp: {resp.json().get("asks", ["empty"])[-1]}"
        else:
            # print(f"No valid y/n asks returned")
            return f"Not valid y/n asks, market: {m['mkt_question']}, y_clob_token: {"https://clob.polymarket.com/book?token_id={clob_tokens[0]}"}, n_clob_token: {"https://clob.polymarket.com/book?token_id={clob_tokens[1]}"}, thread: {threading.current_thread().name}"
    else:
        # print(f"No clob data returned")
        return f"No clob data returned, market: {m['mkt_question']}, y_clob_token: {"https://clob.polymarket.com/book?token_id={clob_tokens[0]}"}, n_clob_token: {"https://clob.polymarket.com/book?token_id={clob_tokens[1]}"}, thread: {threading.current_thread().name}"


def fetch_gamma(url):
    start = time.time()
    gamma_limiter.acquire()
    events = requests.get(url)

    try:
        if events:
            # print("-----------------------------------------------------")
            # pp.pprint(evts)
            # print("-----------------------------------------------------")
            # only if there are events returned
            clob_urls = [
                {
                    "clobTokenIds": market["clobTokenIds"],
                    "mkt_question": market["question"],
                    "mkt_slug": market["slug"],
                }
                for event in events.json()
                for market in event["markets"]
                if market["active"]
                # for clob_token in json.loads(market["clobTokenIds"])
            ]
            # print(clob_urls[0])
            # clob_urls = [
            #     f"https://clob.polymarket.com/book?token_id={clob_token}"
            #     for event in events.json()
            #     for market in event["markets"]
            #     if market["active"]
            #     for clob_token in json.loads(market["clobTokenIds"])
            # ]

            with ThreadPoolExecutor(max_workers=20) as clob_executor:
                clob_fut = [
                    clob_executor.submit(fetch_clob, clob_url) for clob_url in clob_urls
                ]
                for c in as_completed(clob_fut):
                    pass
                    # print(c.result())

            # return f"lenght: {clob_urls}, thread: {threading.current_thread().name}"
            return f"lenght: {len(clob_urls)}, start_time: {start}, end_time: {time.time()}, duration: {time.time() - start}, thread: {threading.current_thread().name}"
        else:
            # pass
            return f"No events returned, start_time: {start}, end_time: {time.time()}, duration: {time.time() - start}, thread: {threading.current_thread().name}"
    except Exception as e:
        raise Exception(
            f"Error fetching gamma data: {e}, url: {url}"
            # f"Error fetching gamma data: {e}, url: {url}, events: {[market["slug"] for e in events.json() for market in e["markets"]]}"
        )


gamma_urls = [
    f"https://gamma-api.polymarket.com/events?order=id&ascending=false&active=true&closed=false&limit={GAMMA_PAGE_LEN}&offset={offset}"
    for offset in range(0, 10000, GAMMA_PAGE_LEN)
]

with ThreadPoolExecutor(max_workers=20) as gamma_executor:
    gamma_fut = [
        gamma_executor.submit(fetch_gamma, gamma_url) for gamma_url in gamma_urls
    ]
    for g in as_completed(gamma_fut):
        pass
        # print(g.result())
print("-" * 50)
print("Finished fetching all data.")
print("-" * 50)
# pbar = tqdm()
