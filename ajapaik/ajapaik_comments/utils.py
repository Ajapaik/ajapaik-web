import re

from django.db.models import F

RE_LINKED_IMG = re.compile(
    r"\[!\[([^\]]*)\]\((https?://[^\s\)]+|www\.[^\s\)]+)\)\]\((https?://[^\s\)]+|www\.[^\s\)]+)\)"
)
RE_IMG = re.compile(r"!\[([^\]]*)\]\((https?://[^\s\)]+|www\.[^\s\)]+)\)")
RE_MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s\)]+|www\.[^\s\)]+)(?:\s+\"[^\"]*\")?\)")
RE_AUTOLINK = re.compile(r"<(https?://[^\s>]+)>")
RE_CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
RE_INLINE_CODE = re.compile(r"`[^`]+`")
RE_HTML_TAG = re.compile(r"<[a-zA-Z\/][^>]*>")

RAW_URL_PATTERN = re.compile(
    r"(https?://[^\s<>\"']+|(?<![/a-zA-Z0-9])www\.[^\s<>\"']+)", re.IGNORECASE
)


def convert_raw_urls_to_markdown(text):
    """
    Safely finds raw unformatted URLs and converts them to markdown links [url](url).
    Preserves existing markdown links, images, code blocks, and HTML tags.
    Strips trailing sentence punctuation (. , ; : ! ? ) ] etc.) from URLs.
    """
    if not text:
        return text, False

    tokens = []

    def save_token(m):
        tokens.append(m.group(0))
        return f"___MD_PLACEHOLDER_{len(tokens)-1}___"

    # 1. Protect code blocks, existing markdown links/images, and HTML tags
    t = RE_CODE_BLOCK.sub(save_token, text)
    t = RE_INLINE_CODE.sub(save_token, t)
    t = RE_LINKED_IMG.sub(save_token, t)
    t = RE_IMG.sub(save_token, t)
    t = RE_MD_LINK.sub(save_token, t)
    t = RE_AUTOLINK.sub(save_token, t)
    t = RE_HTML_TAG.sub(save_token, t)

    modified = False

    def replace_url(m):
        nonlocal modified
        raw = m.group(1)
        trail = ""

        # Strip sentence/bracket punctuation from the end of the URL
        while raw:
            last_char = raw[-1]
            if last_char in ".,;:!?\"'":
                trail = last_char + trail
                raw = raw[:-1]
            elif last_char == ")":
                # Unbalanced closing parenthesis: strip it
                if raw.count(")") > raw.count("("):
                    trail = last_char + trail
                    raw = raw[:-1]
                else:
                    break
            elif last_char == "]":
                trail = last_char + trail
                raw = raw[:-1]
            else:
                break

        # Plausible URL structure
        if len(raw) < 5 or ("." not in raw and "/" not in raw):
            return m.group(0)

        modified = True
        target = raw if raw.startswith(("http://", "https://")) else f"https://{raw}"
        return f"[{raw}]({target}){trail}"

    t = RAW_URL_PATTERN.sub(replace_url, t)

    # 2. Restore protected tokens
    for i, tok in enumerate(tokens):
        t = t.replace(f"___MD_PLACEHOLDER_{i}___", tok)

    return t, modified


def get_comment_replies(comment):
    """
    Returns queryset that contain all reply for given comment.
    """
    from django_comments_xtd import get_model

    return get_model().objects.filter(parent_id=comment.pk).exclude(parent_id=F("pk"))

