import requests
import sys
import time

lst = list()
oibull = 0.0
oibear = 0.0
oicall = 0.0
oiput = 0.0

strikepx = dict()

btcidx = requests.get("https://test.deribit.com/api/v2/public/get_index_price?index_name=btc_usd").json()["result"]["index_price"]
#ethidx = requests.get("https://test.deribit.com/api/v2/public/get_index_price?index_name=eth_usd").json()["result"]["index_price"]

ret = requests.get("https://www.deribit.com/api/v2/public/get_instruments?currency=BTC&expired=false&kind=option").json()["result"]

for r in ret:
    time.sleep(1)
    roi = requests.get("https://www.deribit.com/api/v2/public/get_book_summary_by_instrument?instrument_name="+r["instrument_name"]).json()
    print(roi)
    lst.append({
        "strike":r["strike"],
        "type":r["option_type"],
        "expiration":r["expiration_timestamp"],
        "instrument":r["instrument_name"],
        "oi":roi["result"][0]["open_interest"]
        })

    if r["strike"] in strikepx.keys():
        strikepx[r["strike"]]["oitotal"] += roi["result"][0]["open_interest"]
    else:
        strikepx[r["strike"]] = {"oitotal":roi["result"][0]["open_interest"], "oiput":0.0, "oicall":0.0}

    if r["option_type"] == "call":
        oicall += roi["result"][0]["open_interest"]
        strikepx[r["strike"]]["oicall"] += roi["result"][0]["open_interest"]
        if r["strike"] > btcidx:
            oibull += roi["result"][0]["open_interest"]
    else:
        oiput += roi["result"][0]["open_interest"]
        strikepx[r["strike"]]["oiput"] += roi["result"][0]["open_interest"]
        if r["strike"] < btcidx:
            oibear += roi["result"][0]["open_interest"]



newlist = sorted(lst, key=lambda k: k['oi'], reverse=True) 
dd = sorted(strikepx.items(), key= lambda k: k[1]["oitotal"], reverse=True) 

print("The TOP20 Open interest levels:")
for opt in newlist[:20]:
    print("Open interest {}M at {} ; (type:{}, expiration:{})".format(opt["oi"], opt["strike"], opt["type"], time.ctime(opt["expiration"])))

print("The TOP20 Open interest by price levels:")
for opt in dd[:20]:
    #print("Price {} with open interest at {}M ; (type:{}, expiration:{})".format(opt[0])
    print("Price {} ".format(opt))

print("")
print("Total calls open interest: {}".format(oicall))
print("Total puts open interest: {}".format(oiput))
print("Total open interest > current price ({}) : {}".format(btcidx, oibull))
print("Total open interest < current price ({}) : {}".format(btcidx, oibear))
