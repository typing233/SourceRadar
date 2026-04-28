import logging
from typing import List, Any
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..config import settings
from ..models.user import User

logger = logging.getLogger(__name__)


def build_email_html(user: User, content_items: List[Any]) -> str:
    items_html = ""
    for item in content_items:
        source_colors = {
            "github": "#24292e",
            "hackernews": "#ff6600",
            "producthunt": "#da552f",
        }
        color = source_colors.get(item.source, "#666")
        tags_html = "".join(
            f'<span style="background:#f0f0f0;padding:2px 8px;border-radius:12px;font-size:12px;margin-right:4px;">{tag}</span>'
            for tag in (item.tags or [])[:5]
        )
        items_html += f"""
        <div style="border:1px solid #e1e4e8;border-radius:8px;padding:16px;margin-bottom:16px;">
            <div style="margin-bottom:8px;">
                <span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-size:12px;">{item.source.upper()}</span>
                <span style="color:#666;font-size:12px;margin-left:8px;">Score: {item.score}</span>
            </div>
            <h3 style="margin:8px 0;"><a href="{item.url}" style="color:#0366d6;text-decoration:none;">{item.title}</a></h3>
            <p style="color:#586069;margin:8px 0;font-size:14px;">{item.description[:200] if item.description else ''}</p>
            <div style="margin-top:8px;">{tags_html}</div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:600px;margin:0 auto;padding:20px;color:#24292e;">
        <div style="text-align:center;margin-bottom:32px;">
            <h1 style="color:#0366d6;">&#128225; SourceRadar Weekly Report</h1>
            <p style="color:#586069;">Hi {user.username}! Here are your top picks for this week.</p>
        </div>
        <div style="margin-bottom:16px;">
            <p style="color:#586069;">Based on your interests: {', '.join(user.tags or [])}</p>
        </div>
        {items_html}
        <div style="text-align:center;margin-top:32px;color:#586069;font-size:12px;">
            <p>You're receiving this because you have weekly reports enabled.</p>
            <p>Visit <a href="{settings.FRONTEND_URL}">SourceRadar</a> to update your preferences.</p>
        </div>
    </body>
    </html>
    """


async def send_weekly_report_email(user: User, content_items: List[Any]) -> bool:
    subject = "SourceRadar Weekly Report"
    html_content = build_email_html(user, content_items)

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(f"[EMAIL LOG] Would send weekly report to {user.email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Top {len(content_items)} items for user {user.username}")
        for item in content_items[:5]:
            logger.info(f"  - [{item.source}] {item.title} ({item.url})")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL or settings.SMTP_USER
        msg["To"] = user.email
        msg.attach(MIMEText(html_content, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info(f"Weekly report sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {e}")
        return False


async def send_weekly_reports_to_all(db_session) -> None:
    from ..models.user import User
    from ..models.content import Content
    from .recommendation import score_content_for_user
    from datetime import datetime, timedelta

    week_ago = datetime.utcnow() - timedelta(days=7)
    content = db_session.query(Content).filter(Content.created_at >= week_ago).all()
    users = db_session.query(User).filter(User.email_reports == True).all()

    for user in users:
        try:
            scored = score_content_for_user(content, user.tags or [])
            scored.sort(key=lambda x: x[1], reverse=True)
            top_items = [c for c, _ in scored[:20]]
            await send_weekly_report_email(user, top_items)
        except Exception as e:
            logger.error(f"Failed to process report for {user.email}: {e}")
