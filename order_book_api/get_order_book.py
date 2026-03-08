import requests
import pandas as pd
import pprint as pp
import time
import json
from tqdm import tqdm

status = requests.get("https://clob.polymarket.com")
print(f"gamma API status: {status.status_code}")

page_len = 100
offset = 0
count = 0

# pbar = tqdm()

with open("all_events.json", "r") as f:
    markets = json.load(f)
# print(markets[0:5])
# pp.pprint(markets[0:5])

clobs = []

#######################
# All events
#######################
try:
    for market in tqdm(markets):
        clobs.append(
            [
                {
                    "evt_ticker": market["evt_ticker"],
                    "evt_title": market["evt_title"],
                    "mkt_question": market["markets"]["mkt_question"],
                    "mkt_slug": market["markets"]["mkt_slug"],
                    "mkt_clob_tokens": market["markets"]["mkt_clob_tokens"],
                    "ask_prices": [
                        requests.get(
                            f"https://clob.polymarket.com/book?token_id={clob_token}"
                        )
                        .json()
                        .get("asks", ["empty"])[-1]
                        for clob_token in market["markets"]["mkt_clob_tokens"]
                    ],
                }
            ]
        )
        print(market)
        time.sleep(0.0012)
        # pbar.set_postfix(status="running")

    with open("all_clob_prices.json", "w") as f:
        json.dump(clobs, f, indent=2)

    # pbar.close()
except Exception as e:
    print("-------")
    print(market)
    print("-------")
    print(e)
    # pp.pprint(evt)

#######################
# Latest event
#######################
# ob = requests.get(
#     # f"https://clob.polymarket.com/book?token_id=46553455570564517989191023458705371521436514261892866503067981558938998232024"
#     f"https://clob.polymarket.com/book?token_id=102559817034631022221500208641784929295731053857601013029449249654006364919935"
# )
# # pp.pprint(evts.json())
# with open("order_book.json", "w") as f:
#     json.dump(ob.json(), f, indent=2)

#######################
# Event by slug
#######################
# evts = requests.get(
#     f"https://gamma-api.polymarket.com/events?slug=fed-decision-in-march-885"
# )
# pp.pprint(evts.json())
# with open("fed.json", "w") as f:
#     json.dump(evts.json(), f, indent=2)


# event = evts.json()[0]
# pp.pprint(json.dump(event))

# event_df = pd.DataFrame([event])
# print(event_df.head())
