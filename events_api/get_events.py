import requests
import pandas as pd
import pprint as pp
import time
import json
from tqdm import tqdm
from itertools import chain

status = requests.get("https://gamma-api.polymarket.com/status")
print(f"gamma API status: {status.status_code}")

page_len = 100
offset = 0
count = 0

pbar = tqdm()

#######################
# All events
#######################
# markets = []
# try:
#     while page_len == 100:
#         evts = requests.get(
#             f"https://gamma-api.polymarket.com/events?order=id&ascending=false&active=true&closed=false&limit={page_len}&offset={offset}"
#         )
#         # print(evts.headers)
#         events = evts.json()

#         for evt in events:
#             markets.extend(
#                 [
#                     {
#                         "evt_ticker": evt["ticker"],
#                         "evt_title": evt["title"],
#                         "markets": {
#                             "mkt_question": m["question"],
#                             "mkt_slug": m["slug"],
#                             "mkt_clob_tokens": json.loads(m["clobTokenIds"]),
#                         },
#                     }
#                     for m in evt["markets"]
#                     if m["active"]
#                 ]
#             )

#         # for evt in events:
#         #     count += 1

#         time.sleep(0.02)
#         # print(f"page_len: {page_len}, offset: {offset}")
#         page_len = len(events)
#         offset += page_len
#         pbar.update(page_len)
#         # pbar.set_postfix(status="running")

#     pbar.close()
#     print(len(events))
#     with open("all_events.json", "w") as f:
#         json.dump(markets, f, indent=2)
# except Exception as e:
#     print(e)
#     pp.pprint(evt)

#######################
# Latest event
#######################
# evts = requests.get(
#     f"https://gamma-api.polymarket.com/events?order=id&ascending=false&active=true&closed=false&limit=2&offset=50000"
# )
# # pp.pprint(evts.headers)
# pp.pprint(len(evts.json()))
# # with open("events.json", "w") as f:
# #     json.dump(evts.json(), f, indent=2)

#######################
# Event by slug
#######################
events = [
    "kharg-island-no-longer-under-iranian-control-by-march-31",
    "ncaa-tournament-team-to-make-national-championship",
    "ncaa-tournament-team-to-make-semifinals",
    "spl-taa-kho-2026-04-10-more-markets",
    "spl-njm-neo-2026-04-10-more-markets",
    "spl-sha-ith-2026-04-10-more-markets",
    "ncaa-tournament-team-to-make-elite-eight",
    "where-will-kirk-cousins-play-in-2026-27",
    "ncaa-tournament-team-to-make-sweet-sixteen",
    "will-kanye-tweet-again-by-march-31",
]

evts = [
    requests.get(f"https://gamma-api.polymarket.com/events?slug={slug}")
    for slug in events
]

# evts = requests.get(
#     f"https://gamma-api.polymarket.com/events?slug=fed-decision-in-march-885"
# )
# pp.pprint(evts.json())
with open("events_by_slug.json", "w") as f:
    json.dump(list(chain.from_iterable([evt.json() for evt in evts])), f, indent=2)


# # event = evts.json()[0]
# # pp.pprint(json.dump(event))

# event_df = pd.DataFrame([event])
# print(event_df.head())
