import requests
import datetime
import os


def send_sms(text_content):
    from twilio.rest import Client
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body=text_content,
        from_=os.environ["TWILIO_NUMBER"],
        to=os.environ["MY_NUMBER"]
    )


# Getting today's date
today_date = datetime.datetime.today() - datetime.timedelta(days=1)
today = today_date.strftime("%Y-%m-%d")
yesterday_date = datetime.datetime.today() - datetime.timedelta(days=2)
yesterday = yesterday_date.strftime("%Y-%m-%d")

# Fetch Stock Api
STOCK = "TSLA"
COMPANY_NAME = "TeslaInc"
STOCK_API_KEY = os.environ["ALPHAVANTAGE_API_KEY"]
STOCK_API = "https://www.alphavantage.co/query"
stocks_param = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY,
}
stocks_response = requests.get(STOCK_API, params=stocks_param)
stocks_response.raise_for_status()
stocks_data = stocks_response.json()
today_stock_value = float(stocks_data["Time Series (Daily)"][today]["4. close"])
yesterday_stock_value = float(stocks_data["Time Series (Daily)"][yesterday]["4. close"])

# Fetch news api
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
NEWS_API = "https://newsapi.org/v2/everything"
news_param = {
    "q": COMPANY_NAME,
    "from": yesterday,
    "to": today,
    "sortBy": "popularity",
    "apiKey": NEWS_API_KEY,
}
news_response = requests.get(NEWS_API, params=news_param)
news_response.raise_for_status()
news_data = news_response.json()["articles"]
for article in news_data:
    article_split = article["title"].split(" ")
    if "Tesla" in article_split:
        news_article_index = news_data.index(article)
        break

news_article = news_data[news_article_index]
headline = news_article["title"]
brief = news_article["description"]
url = news_article["url"]

percentage = round((today_stock_value - yesterday_stock_value) / yesterday_stock_value * 100, 2)
if percentage > 0:
    content = f"{STOCK}: 🔺 {percentage}% \n" \
              f"Headline: {headline}\n" \
              f"Brief: {brief}\n" \
              f"To Know more refer to this URL\n" \
              f"URL: {url}"
    send_sms(content)
elif percentage < 0:
    content = f"{STOCK}: 🔻 {abs(percentage)}% \n" \
              f"Headline: {headline}\n" \
              f"Brief: {brief}\n" \
              f"To Know more refer to this URL\n" \
              f"URL: {url}"
    send_sms(content)