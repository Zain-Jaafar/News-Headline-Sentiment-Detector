import requests
import xml.etree.ElementTree as ET
import pandas
import seaborn
import matplotlib.pyplot as plt
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS


RSS_FEED_URL = "https://feeds.bbci.co.uk/news/rss.xml"
rss_feed_file = "rss_feed.xml"

response = requests.get(RSS_FEED_URL)

with open(rss_feed_file, "wb") as file:
    file.write(response.content)

tree = ET.parse(rss_feed_file)
root = tree.getroot()

news_items = []

for item in root.findall("./channel/item"):
    for child in item:
        if child.tag == "title":
            title = child.text
        elif child.tag == "description":
            description = child.text
        elif child.tag == "link":
            link = child.text
        elif child.tag == "pubDate":
            pub_date = child.text
        
    news_items.append({
        "title": title,
        "description": description,
        "link": link,
        "pub_date": pub_date,
    })

df = pandas.DataFrame(news_items)
df["pub_date"] = pandas.to_datetime(df["pub_date"]) 

article_subjectivity = []
article_polarity = []


for _, article in df.iterrows():
    article_sentiment = TextBlob(f"{article["title"]}. {article["description"]}").sentiment

    article_subjectivity.append(article_sentiment.subjectivity)
    article_polarity.append(article_sentiment.polarity)

df["subjectivity"] = article_subjectivity
df["polarity"] = article_polarity

def determine_polarity_type(polarity_value: int) -> str:
    if polarity_value > 0.2:
        return "Positive"
    elif polarity_value < -0.2:
        return "Negative"
    # Else the article is neutral
    return "Neutral"

def determine_subjectivity_type(subjectivity_value: int) -> str:
    if subjectivity_value >= 0.75:
        return "Subjective"
    elif subjectivity_value >= 0.5:
        return "Fairly Subjective"
    elif subjectivity_value >= 0.25:
        return "Slightly Subjective"
    # Else the article is objective (relatively)
    return "Objective"

df["polarity_categorised"] = df["polarity"].apply(determine_polarity_type)
df["subjectivity_categorised"] = df["subjectivity"].apply(determine_subjectivity_type)

print(df)

plt.figure()
seaborn.barplot(data=df["polarity_categorised"])
plt.title("Polarity Categorised")

plt.figure()
seaborn.barplot(data=df["subjectivity_categorised"])
plt.title("Subjectivity Categorised")

plt.figure()
seaborn.barplot(data=article_subjectivity)
plt.title("Subjectivity")

plt.figure()
seaborn.barplot(data=article_polarity)
plt.title("Polarity")

article_text = " ".join(df["title"].astype(str) + " " + df["description"].astype(str)) 

wordcloud = WordCloud(
    width=800, height=800,
    background_color="white",
    stopwords=STOPWORDS,
    colormap="viridis"
).generate(article_text)

plt.figure(figsize=(12,6))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")

plt.show()

