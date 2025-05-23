# feeds.py - Bee Ticker v5.6 clean architecture (no canvas, no mousewheel binding)


from ttkbootstrap import ttk
import webbrowser
from utils import format_time
from storage import is_saved, toggle_save
import feedparser

# --- Font styles for consistency ---
TITLE_FONT = ("Arial", 10, "bold")
REGULAR_FONT = ("Arial", 10)
ITALIC_FONT = ("Arial", 8, "italic")

# --- Style for article frames and labels ---


FEEDS = {
    "Google News": "https://news.google.com/rss/search?q=honeybee+OR+beekeeping&hl=en-US&gl=US&ceid=US:en",
    "Bee Culture": "https://www.beeculture.com/feed/",
    "American Bee Journal": "https://americanbeejournal.com/feed/"
}

ARTICLES_PER_PAGE = 4  # or whatever fits your layout

def get_articles():
    articles = []
    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published if "published" in entry else "",
                "source": source
            })
    return articles

def create_feed_frame(app, page=0):
    frame = ttk.Frame(app.content_area)

    articles = get_articles()
    total_pages = max(1, (len(articles) + ARTICLES_PER_PAGE - 1) // ARTICLES_PER_PAGE)
    start = page * ARTICLES_PER_PAGE
    end = start + ARTICLES_PER_PAGE
    page_articles = articles[start:end]

    if not page_articles:
        msg = ttk.Label(frame, text="No articles available.", font=REGULAR_FONT)
        msg.pack(pady=20)
        return frame

    for article in page_articles:
        title = article["title"]
        link = article["link"]
        published = article["published"]
        source = article["source"]

        article_frame = ttk.Frame(
            frame,
            padding=10,
            style="Article.TFrame",
            relief="flat",
            borderwidth=0
        )
        article_frame.pack(fill="x", padx=8, pady=8)

        link_label = ttk.Label(
            article_frame,
            text=title,
            cursor="hand2",
            wraplength=220,
            justify="left",
            font=TITLE_FONT,
            style="Article.TLabel"
        )
        link_label.pack(side="top", anchor="w", fill="x", pady=4)
        link_label.bind("<Button-1>", lambda e, url=link: webbrowser.open_new(url))

        info_frame = ttk.Frame(article_frame, style="Article.TFrame")
        info_frame.pack(side="top", fill="x", pady=2)

        source_label = ttk.Label(info_frame, text=source, font=ITALIC_FONT, style="Article.TLabel")
        source_label.pack(side="left", padx=4)

        published_label = ttk.Label(info_frame, text=format_time(published), font=REGULAR_FONT, style="Article.TLabel")
        published_label.pack(side="left", padx=10)

        star_btn = ttk.Button(
            info_frame,
            text="★" if is_saved(title, link, source) else "☆",
            width=2,
            bootstyle="warning",
        )
        star_btn.config(command=lambda t=title, l=link, s=source, btn=star_btn: toggle_star(t, l, s, btn))
        star_btn.pack(side="right")

    # Pagination controls
    nav_frame = ttk.Frame(frame)
    nav_frame.pack(pady=10)

    if page > 0:
        prev_btn = ttk.Button(nav_frame, text="Previous", command=lambda: app.swap_content(create_feed_frame(app, page-1)))
        prev_btn.pack(side="left", padx=5)
    if end < len(articles):
        next_btn = ttk.Button(nav_frame, text="Next", command=lambda: app.swap_content(create_feed_frame(app, page+1)))
        next_btn.pack(side="right", padx=5)

    return frame

def toggle_star(title, link, source, btn):
    toggle_save(title, link, source)
    btn.config(text="★" if is_saved(title, link, source) else "☆")

def schedule_feed_refresh(app, interval=1800):
    app.swap_content(create_feed_frame(app, page=0))
    app.after(interval * 1000, lambda: schedule_feed_refresh(app, interval))
# Call this once in your app init: schedule_feed_refresh(self)

