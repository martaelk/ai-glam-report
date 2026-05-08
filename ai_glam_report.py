import feedparser
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

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

# Email settings
EMAIL_FROM = "marmat.rtu@gmail.com"
import os
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

EMAIL_TO = [
    "marmat.rtu@gmail.com",
    "marta.kivkule@lnb.lv",
    "aija.uzula@lnb.lv",
    "matiss.bolsteins@lnb.lv",
]


def fetch_news():
    articles = []

    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")

            text = f"{title} {summary}".lower()

            if any(keyword.lower() in text for keyword in KEYWORDS):
                articles.append({
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "source": feed.feed.get("title", "Unknown source")
                })

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

    print(f"Found {len(articles)} relevant articles")

    html = build_html_report(articles)

    print("Sending email...")

    send_email(html)

    print("Done!")


if __name__ == "__main__":
    main()