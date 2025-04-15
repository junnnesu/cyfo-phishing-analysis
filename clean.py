import json
import re
from email.utils import parseaddr, getaddresses
from dateutil import parser as date_parser
from dateutil.tz import UTC

INPUT_JSON = "parser_output.json"
OUTPUT_JSON = "cleaned_emails.json"

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def clean_email_address(raw):
    email = parseaddr(raw)[1].strip().lower()
    return email if EMAIL_REGEX.match(email) else None

def clean_receivers(raw_list):
    if not raw_list or not isinstance(raw_list, list):
        return []
    addresses = getaddresses([(x if isinstance(x, str) else "") for x in raw_list])
    cleaned = {addr.strip().lower() for name, addr in addresses if EMAIL_REGEX.match(addr.strip().lower())}
    return sorted(cleaned)

def clean_date(date_str):
    try:
        dt = date_parser.parse(date_str)
        dt_utc = dt.astimezone(UTC)
        return dt_utc.isoformat()
    except Exception:
        return None

def clean_all():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        raw_emails = json.load(f)

    cleaned_emails = []

    for entry in raw_emails:
        cleaned = {
            "file": entry.get("file", ""),
            "sender": clean_email_address(entry.get("sender", "")),
            "receivers": clean_receivers(entry.get("receivers", [])),
            "subject": entry.get("subject", "").strip(),
            "date": entry.get("date", "").strip(),
            "clean_date": clean_date(entry.get("date", "")),
            "body_text": entry.get("body_text", "").strip(),
            "body_html": entry.get("body_html", "").strip(),
            "attachments": entry.get("attachments", []),
            "attachment_types": [t.strip().lower() for t in entry.get("attachment_types", []) if isinstance(t, str)],
            "ip": entry.get("ip") or None
        }

        if "error" in entry:
            cleaned["error"] = entry["error"]

        cleaned_emails.append(cleaned)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned_emails, f, indent=2, ensure_ascii=False)

    print(f"✅ Cleaned {len(cleaned_emails)} emails → {OUTPUT_JSON}")

if __name__ == "__main__":
    clean_all()
