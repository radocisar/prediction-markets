import requests
import pandas as pd
import pprint as pp
import time
import json
from tqdm import tqdm

status = requests.get("https://gamma-api.polymarket.com/status")
print(f"gamma API status: {status.status_code}")

page_len = 100
offset = 0
count = 0

pbar = tqdm()

#######################
# All events
#######################
markets = []
try:
    while page_len == 100:
        evts = requests.get(
            f"https://gamma-api.polymarket.com/events?order=id&ascending=false&active=true&closed=false&limit={page_len}&offset={offset}"
        )
        # print(evts.headers)
        events = evts.json()

        for evt in events:
            markets.extend(
                [
                    {
                        "evt_ticker": evt["ticker"],
                        "evt_title": evt["title"],
                        "markets": {
                            "mkt_question": m["question"],
                            "mkt_slug": m["slug"],
                            "mkt_clob_token": json.loads(m["clobTokenIds"])[0],
                        },
                    }
                    for m in evt["markets"]
                    if m["active"]
                ]
            )

        # for evt in events:
        #     count += 1

        time.sleep(0.02)
        page_len = len(events)
        offset += page_len
        pbar.update(page_len)
        # pbar.set_postfix(status="running")

    pbar.close()
    print(len(events))
    with open("all_events.json", "w") as f:
        json.dump(markets, f, indent=2)
except Exception as e:
    print(e)
    pp.pprint(evt)
#######################
# Latest event
#######################
# evts = requests.get(
#     f"https://gamma-api.polymarket.com/events?order=id&ascending=false&active=true&closed=false&limit=1&offset=0"
# )
# # pp.pprint(evts.json())
# with open("events.json", "w") as f:
#     json.dump(evts.json(), f, indent=2)

#######################
# Event by slug
#######################
# evts = requests.get(
#     f"https://gamma-api.polymarket.com/events?slug=fed-decision-in-march-885"
# )
# # pp.pprint(evts.json())
# with open("fed.json", "w") as f:
#     json.dump(evts.json(), f, indent=2)


# event = evts.json()[0]
# pp.pprint(json.dump(event))

# event_df = pd.DataFrame([event])
# print(event_df.head())
