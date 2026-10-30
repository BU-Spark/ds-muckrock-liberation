"""Standard text cleaning for FOIA text columns (API, XML or foia.gov CSV).

Run every text column through clean_text() when building the final tables.
It only changes formatting (HTML codes, quotes, whitespace, N/A spelling), never the content.
Do not use it on number columns.

Not done on purpose:
- No Unicode normalization (NFKC): it breaks characters such as a mistyped "¸" (meant as a comma).
- "None" is not changed to "N/A": "none" and "not applicable" mean different things.

    from foia_text import clean_text
    df[col] = df[col].map(clean_text)
"""
import html
import re

ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);")
QUOTES = str.maketrans({"“": '"', "”": '"', "„": '"', "″": '"',
                        "‘": "'", "’": "'", "‚": "'", "′": "'"})
NA_SPELLINGS = {"n/a", "na", "n\\a", "n.a."}


def clean_text(v, max_rounds=3):
    if v is None:
        return ""
    s = str(v)
    # 1. HTML codes; some reports are escaped two or three times (&amp;quot;)
    for _ in range(max_rounds):
        if not ENTITY.search(s):
            break
        s = html.unescape(s)
    # 2. curly quotes -> straight quotes
    s = s.translate(QUOTES)
    # 3. line breaks, tabs, non-breaking and repeated spaces -> one space
    s = re.sub(r"\s+", " ", s).strip()
    # 4. other spellings of N/A (n/a, NA, N\A) -> "N/A"
    if s.lower() in NA_SPELLINGS:
        s = "N/A"
    return s


def leftover_entities(s):
    """HTML codes still left after cleaning (should be none; used as an update check)."""
    return ENTITY.findall(s)
