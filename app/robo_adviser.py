import csv
from dotenv import load_dotenv
import json
import os
import requests
import datetime
import pytest

# FUNCTIONS FIRST

# turns string to dict
# we loop through dates (and their attributes: prices)
# create new dict with dates' attributes/prices
# add new dictionary items to list
def parse_response(response_text):
    # response_text can be either a raw JSON string or an already-converted dictionary
    if isinstance(response_text, str): # if not yet converted, then:
        response_text = json.loads(response_text)  # convert string to dictionary

        results = []
        time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
        for trading_date in time_series_daily:
            prices = time_series_daily[trading_date]
            result = {
                "date": trading_date,
                "open": prices["1. open"],
                "high": prices["2. high"],
                "low": prices["3. low"],
                "close": prices["4. close"],
                "volume": prices["5. volume"]
            }
            results.append(result)
        return results


# write to csv
def write_prices_to_file(prices=[], filename="data/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"],
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)

# find most recent closing price
def latest_closing_price(dates_dict):
    latest_date = daily_prices[0]["date"]
    latest_closing_price = daily_prices[0]["close"]
    latest_closing_price = "{0:,.2f}".format(float(latest_closing_price))
    return latest_closing_price

# find highest avg max price
def max_high_price(dates_dict):
    counter = 0
    prices_100_list = []
    if counter < 100:
        for date in daily_prices:
            prices_100_list.append(float(date["high"]))
            counter += 1

    max_high_price = max(prices_100_list)
    max_high_price = "{0:,.2f}".format(float(max_high_price))
    return max_high_price

# find lowest avg min price
def min_low_price(dates_dict):
    counter = 0
    prices_100_list = []
    if counter < 100:
        for date in daily_prices:
            prices_100_list.append(float(date["low"]))
            counter += 1

    min_low_price = min(prices_100_list)
    min_low_price = "{0:,.2f}".format(float(min_low_price))
    return min_low_price

# recommend buy/don't buy + explanation
def buy_sell_recco(dates_dict):
    if float(latest_closing_price) < (1.2 * float(min_low_price)):
        return (f"BUY\n+ Why? Because {symbol.upper()}'s latest closing price (${latest_closing_price}) is less than 20% above its recent average low price (${min_low_price}).")
    else:
        return (f"DO NOT BUY\n+ Why? Because {symbol.upper()}'s latest closing price (${latest_closing_price}) is more than 20% above its recent average low price (${min_low_price}).")


# only execute if file invoked from the command-line; not when imported into other files, like tests
if __name__ == '__main__':

# user inputs stock symbol
    symbol = input("Please input a stock symbol (e.g. 'NFLX'): ")

# VALIDATION 1 - VALID STOCK SYMBOL-TYPE ENTRY [NO REQUEST]
    try:
        float(symbol)
        quit("NOT VALID. EXPECTING NON-NUMERIC SYMBOL")
    except ValueError as e:
        pass

# load environmental var
    load_dotenv()
# INFORMATION INPUT
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

# ASSEMBLE REQUEST URL
    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

# ISSUE "GET" REQUEST
    response = requests.get(request_url)

# VALIDATION 2 - EXISTING STOCK SYMBOL [DURING REQUEST]
    if "Error Message" in response.text:
        print("REQUEST ERROR - PLEASE TRY AGAIN. CHECK YOUR STOCK SYMBOL.")
        quit("Stopping the program.")

# INFORMATION OUTPUT 1 - WRITE TO CSV
# function: convert string to dict
    daily_prices = parse_response(response.text)
# function: write to CSV
    write_prices_to_file(prices=daily_prices, filename="data/prices.csv")

# INFORMATION OUTPUT 2 - CALCULATIONS
# load current date+time
    now = datetime.datetime.now()
    # TODO: make latest_date look like a nice format

    # SET VARIABLES FOR PRINTING, USING FUNCTIONS
    latest_date = daily_prices[0]["date"]
    latest_closing_price = latest_closing_price(dates_dict=daily_prices)
    max_high_price = max_high_price(dates_dict=daily_prices)
    min_low_price = min_low_price(dates_dict=daily_prices)
    buy_sell_recco = buy_sell_recco(dates_dict=daily_prices)

    # PRINT CALCULATIONS + RECOMMENDATION
    print(f"- {symbol.upper()} -")
    print(now.strftime("This program was run: %B %d, %Y at %I:%M:%S %p"))
    print(f"Latest data from: {latest_date}")
    print("----------")
    print(f"+ Latest Closing Price: ${latest_closing_price}")
    print(f"+ Recent Average High Price: ${max_high_price}")
    print(f"+ Recent Average Low Price: ${min_low_price}")
    print(f"+ Recommendation: {buy_sell_recco}")
