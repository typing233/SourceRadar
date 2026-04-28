import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, BaseLoader

from app.config import settings

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: system-ui, sans-serif; background: #f9f9fb; color: #1a1a2e; margin: 0; padding: 0; }
  .container { max-width: 620px; margin: 32px auto; background: #fff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 12px rgba(0,0,0,.07); }
  h1 { color: #6366f1; margin-top: 0; }
  .item { border-bottom: 1px solid #eee; padding: 16px 0; }
  .item:last-child { border-bottom: none; }
  .item a { color: #6366f1; font-size: 1.05em; font-weight: 600; text-decoration: none; }
  .item a:hover { text-decoration: underline; }
  .badge { display: inline-block; background: #ede9fe; color: #4f46e5; border-radius: 6px; padding: 2px 8px; font-size: .8em; margin-left: 6px; }
  .stars { color: #f59e0b; }
  .desc { color: #555; font-size: .92em; margin: 4px 0; }
  .tags { font-size: .8em; color: #888; }
  .footer { color: #aaa; font-size: .8em; margin-top: 24px; }
</style>
</head>
<body>
<div class="container">
  <h1>🚀 SourceRadar Weekly Digest</h1>
  <p>Hi {{ email }}, here are your top {{ items|length }} picks this week:</p>

  {% for entry in items %}
  <div class="item">
    <a href="{{ entry.url }}" target="_blank">{{ entry.title }}</a>
    <span class="badge">{{ entry.source }}</span>
    <br>
    <span class="stars">{{ "★" * [5, (entry.match_score * 5)|int]|min }}{{ "☆" * (5 - [5, (entry.match_score * 5)|int]|min) }}</span>
    <p class="desc">{{ entry.description[:200] }}{% if entry.description|length > 200 %}…{% endif %}</p>
    {% if entry.raw_tags %}
    <p class="tags">🏷 {{ entry.raw_tags | join(", ") }}</p>
    {% endif %}
  </div>
  {% endfor %}

  <div class="footer">
    You're receiving this because you have digests enabled on SourceRadar.<br>
    To unsubscribe, log in and disable "Receive weekly digest" in Settings.
  </div>
</div>
</body>
</html>
"""

_jinja_env = Environment(loader=BaseLoader())
_template = _jinja_env.from_string(EMAIL_TEMPLATE)


async def send_digest_email(user, digest) -> None:
    if not settings.SMTP_USER or not settings.SMTP_HOST:
        return

    items = []
    for di in digest.digest_items:
        item = di.item
        items.append(
            {
                "title": item.title,
                "url": item.url,
                "description": item.description or "",
                "source": item.source,
                "raw_tags": item.get_raw_tags(),
                "match_score": di.match_score,
            }
        )
    items.sort(key=lambda x: x["match_score"], reverse=True)

    html = _template.render(email=user.email, items=items)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your SourceRadar Weekly Digest"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = user.email
    msg.attach(MIMEText(html, "html"))

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
