import feedparser
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import json
from pathlib import Path

# News sources
FEEDS = [
    "https://openai.com/news/rss.xml",
    "https://www.anthropic.com/news/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://blogs.loc.gov/thesignal/feed/",
]

# Keywords relevant to AI + GLAM
KEYWORDS = [
    "ChatGPT", "OpenAI", "GPT", "AI model","Gemini","Claude","Anthropic",
    "library", "libraries",
    "archive", "archives",
    "museum", "museums",
    "GLAM",
    "cultural heritage",
    "digitization",
    "digitisation",
    "OCR",
    "metadata",
    "collections",
    "accessibility",
]

HISTORY_FILE = "sent_articles.json"
MAX_HISTORY = 500

# Email settings
EMAIL_FROM = "marmat.rtu@gmail.com"
import os
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

EMAIL_TO = [
    "marta.kivkule@lnb.lv",
    "aija.uzula@lnb.lv",
    "matiss.bolsteins@lnb.lv",
    "edite.punka@lnb.lv",
]

def load_sent_articles():
    if Path(HISTORY_FILE).exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_sent_articles(sent_articles):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sent_articles[-MAX_HISTORY:], f, indent=2)


def normalize_title(title):
    return title.strip().lower()

def fetch_news():
    articles = []

    sent_articles = load_sent_articles()

    sent_urls = {item["url"] for item in sent_articles}
    sent_titles = {normalize_title(item["title"]) for item in sent_articles}

    new_history_entries = []

    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")

            text = f"{title} {summary}".lower()

            if not any(keyword.lower() in text for keyword in KEYWORDS):
                continue

            normalized = normalize_title(title)

            # Skip duplicates
            if link in sent_urls or normalized in sent_titles:
                print(f"Skipping duplicate: {title}")
                continue

            article = {
                "title": title,
                "summary": summary,
                "link": link,
                "source": feed.feed.get("title", "Unknown source")
            }

            articles.append(article)

            new_history_entries.append({
                "title": title,
                "url": link,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # Save updated history
    sent_articles.extend(new_history_entries)
    save_sent_articles(sent_articles)

    return articles


def build_html_report(articles):
    today = datetime.now().strftime("%d %B %Y")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h1>Mākslīgā intelekta dienas apskats bibliotēkām un kultūras mantojumam</h1>

        <p><strong>Datums:</strong> {today}</p>

        <h2>Aktuālākās ziņas</h2>
    """

    if not articles:
        html += "<p>Šodien nav atrastas atbilstošas ​​ziņas.</p>"

    for article in articles:
        html += f"""
        <div style="margin-bottom: 20px;">
            <h3>{article['title']}</h3>

            <p>
            <strong>Avots:</strong> {article['source']}
            </p>

            <p>
            {article['summary'][:500]}
            </p>

            <p>
            <a href="{article['link']}">Lasīt vairāk</a>
            </p>

            <hr>
        </div>
        """

    html += """
    </body>
    </html>
    """

    return html


def send_email(html):
    msg = MIMEMultipart("alternative")

    msg["Subject"] = "MI aktuālie jaunumi"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_FROM
    msg["Bcc"] = ", ".join(EMAIL_TO)

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)


def main():
    print("Fetching news...")

    articles = fetch_news()

    print(f"Found {len(articles)} new relevant articles")

    # Do not send empty emails
    if not articles:
        print("No new articles found. Email will not be sent.")
        return

    html = build_html_report(articles)

    print("Sending email...")

    send_email(html)

    print("Done!")

if __name__ == "__main__":
    main()