import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pydeck as pdk
from wordcloud import WordCloud, STOPWORDS

st.title("Sentiment Analysis of Tweets about US Airlines")
st.sidebar.title("Sentiment Analysis of Tweets about US Airlines")

st.markdown("This app is a dashboard for Sentiment Analysis of Tweets about US Airlines ✈️")
st.sidebar.markdown("This app is a dashboard for Sentiment Analysis of Tweets about US Airlines ✈️")

@st.cache(persist=True)
def load_data():
    data = pd.read_csv("Tweets.csv")
    data["tweet_created"] = pd.to_datetime(data["tweet_created"])
    return data

data = load_data()
# st.write(data) # Displays data on screen

st.sidebar.subheader("Show random tweet")
random_tweet = st.sidebar.radio("Sentiment type:", ("positive", "neutral", "negative"))
text = data.loc[data["airline_sentiment"] == random_tweet, "text"].sample(n=1).values[0]
st.sidebar.markdown(text)

st.sidebar.subheader("Plot number of tweets by sentiment")
select = st.sidebar.selectbox("Select visualization type:", ["Bar Plot", "Pie Chart"], key=1)
sentiment_count = data["airline_sentiment"].value_counts().to_frame().reset_index()
sentiment_count = sentiment_count.rename(columns = {
    "index": "sentiment",
    "airline_sentiment": "tweets"
})

if not st.sidebar.checkbox("Hide", True, key=2):
    if select == "Bar Plot":
        st.markdown("Bar Plot of the number of tweets")
        fig = px.bar(
            sentiment_count,
            x="sentiment",
            y="tweets",
            color="tweets",
            text="tweets"
        )
        st.plotly_chart(fig)

    elif select == "Pie Chart":
        st.markdown("Pie Chart of the number of tweets")
        fig = px.pie(
            sentiment_count,
            names="sentiment",
            values="tweets",
            color="tweets"
        )
        st.plotly_chart(fig)

st.sidebar.subheader("When and where are users tweeting from?")
hour = st.sidebar.slider("Hour of the day", 0, 23)
hourly_data = data[data["tweet_created"].dt.hour == hour][["airline", "latitude", "longitude"]]

if not st.sidebar.checkbox("Hide", True, key=3):
    st.markdown("Tweets across US based on hour of day")
    st.markdown("{} tweets between {}:00 and {}:00".format(hourly_data.shape[0], hour, (hour+1)%24))

    # midpoint = (np.average(hourly_data["latitude"]), np.average(hourly_data["longitude"]))
    # st.write(pdk.Deck(
    #     map_style = "mapbox://styles/mapbox/light-v9",
    #     initial_view_state = {
    #         "latitude": midpoint[0],
    #         "longitude": midpoint[1],
    #         "zoom": 11,
    #         "pitch": 50
    #     },
    #     layers=[
    #         pdk.Layer(
    #             "HexagonLayer",
    #             data=hourly_data,
    #             get_position=["latitude", "longitude"],
    #             radius=200,
    #             extruded=True,
    #             pickable=True,
    #             elevation_scale=4,
    #             elevation_rage=[0, 1000]
    #         )
    #     ]
    # ))

    st.map(hourly_data)
    if st.sidebar.checkbox("Show raw data", False):
        st.write(hourly_data)

st.sidebar.subheader("Breakdown airline tweets by sentiment")
choice = st.sidebar.multiselect("Pick airlines", tuple(set(data["airline"])))
if len(choice) > 0:
    airline_data = data[data["airline"].isin(choice)][["airline", "airline_sentiment"]]
    fig = px.histogram(
        airline_data,
        x="airline",
        y="airline_sentiment",
        histfunc="count",
        color="airline_sentiment",
        facet_col="airline_sentiment",
        labels={"airline_sentiment": "tweets"},
        height=600,
        width=800
    )
    st.plotly_chart(fig)

st.sidebar.subheader("Word Cloud")
word_sentiment = st.sidebar.radio("Display word cloud for which sentiment?", ("positive", "neutral", "negative"))
if not st.sidebar.checkbox("Hide", True, key=4):
    st.markdown("Word Cloud for {} sentiment".format(word_sentiment))
    sentiment_data = data[data["airline_sentiment"] == word_sentiment]["text"]
    words = " ".join(sentiment_data)
    processed_words = " ".join([word for word in words.split() if "http" not in word and not word.startswith("@") and word != "RT"])
    wordcloud = WordCloud(
        stopwords=STOPWORDS,
        background_color="white",
        height=650,
        width=800
    ).generate(processed_words)
    plt.imshow(wordcloud)
    plt.xticks([])
    plt.yticks([])
    st.pyplot()


