from tkinter import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as st
from geopy.geocoders import Nominatim
import snscrape.modules.twitter as sntwitter
import pandas as pd
import geocoder
import datetime
import re

def system():
    keyword = keyword_input.get()
    print(keyword)
    city = city_input.get()
    print(city)
    r = range_input.get()
    print(r)
    limit = int(t_limit.get())
    g = geocoder.ip('me')
    global geocode
    if city != '0':
        geolocator = Nominatim(user_agent='alvinLi')
        location = geolocator.geocode(city)
        lat = str(location.latitude)
        log = str(location.longitude)
    else:
        lat = str(g.latlng[0])
        log = str(g.latlng[1])

    geocode = lat + ', ' + log + ', {r}'.format(r=r)
    print(geocode)
    today = datetime.date.today()
    global today_date
    today_date = today.strftime("%Y-%m-%d")
    query = '"{k}" geocode:"{j}" until:"{i}" since:2021-01-01'.format(j=geocode, i=today_date, k=keyword)
    tweets = []
    limits = limit
    print(limits)
    for tweet in sntwitter.TwitterSearchScraper(query).get_items():
        if len(tweets) == limits:
            break
        else:
            tweets.append([tweet.date, tweet.user.username, tweet.content, tweet.user.location])

    df = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet', 'location'])

    def clean_Text(text):
        text = re.sub("(@[A-Za-z0-9_]+)", '', str(text))
        text = re.sub(r'#', '', text)
        text = re.sub(r'RT[\s]+', '', text)
        text = re.sub(r'https?:\/\/\S+', '', text)
        return text

    df['Tweet'] = df['Tweet'].apply(clean_Text)
    analyzer = st()

    score_neutral = []
    score_positive = []
    score_negative = []
    score_compound = []
    for i in range(0, df.shape[0]):
        score = analyzer.polarity_scores(df.iloc[i][2])
        score1 = score['neu']
        score_neutral.append(score1)
        score2 = score['pos']
        score_positive.append(score2)
        score3 = score['neg']
        score_negative.append(score3)
        score4 = score['compound']
        score_compound.append(score4)

    df['neutral'] = score_neutral
    df['positive'] = score_positive
    df['negative'] = score_negative
    df['compound'] = score_compound

    for i in range(0, len(df)):
        if df.loc[i, 'compound'] >= 0.05:
            df.loc[i, 'result'] = 'positive'
        elif -0.05 < df.loc[i, 'compound'] < 0.05:
            df.loc[i, 'result'] = 'neutral'
        elif df.loc[i, 'compound'] <= -0.05:
            df.loc[i, 'result'] = 'negative'

    positive = 0
    negative = 0
    neutral = 0

    for i in range(len(df)):
        if df.loc[i, 'result'] == 'positive':
            positive += 1
        elif df.loc[i, 'result'] == 'negative':
            negative += 1
        elif df.loc[i, 'result'] == 'neutral':
            neutral += 1

    text.insert(END, '{k}: '.format(k=keyword))
    text.insert(END, 'Total tweets: ' + str(len(df)))
    text.insert(END, 'Positive: ' + str(positive))
    text.insert(END, 'Negative: ' + str(negative))
    text.insert(END, 'Neutral: ' + str(neutral))
    text.insert(END, '')


root = Tk()
root.title('Tweet Analyzer')
root.geometry('700x300+398+279')
Label(root, text='Insert keywords you want to use:').grid(row=0, column=3)
Label(root, text='City Name (Put 0 if use current location)').grid(row=2, column=3)
Label(root, text='Tweets limit').grid(row=4, column=3)
Label(root, text='search range (use km as the distance unit)').grid(row=6, column=3)
global keyword_input
keyword_input = Entry(root)
keyword_input.grid(row=1, column=3)
global city_input
city_input = Entry(root)
city_input.grid(row=3, column=3)
global t_limit
t_limit = Entry(root)
t_limit.grid(row=5, column=3)
global range_input
range_input = Entry(root)
range_input.grid(row=7, column=3)
global text
text = Listbox(root, width=55, height=10)
text.grid(rowspan=20, row=1, columnspan=3)
Button(root, text='Auto', command=system).grid(row=25, column=0, sticky=W)
Button(root, text='Quit', command=root.quit).grid(row=25, column=2, sticky=E)
root.mainloop()
