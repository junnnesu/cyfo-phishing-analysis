import os
import email
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parseaddr
import json
import re

# ===== 配置 =====
MAIL_DIR = "/forensics/cyfo-forensics/spam_emails"
OUTPUT_JSON = "parser_output.json"

def extract_ip_from_headers(received_headers):
    """从 Received: 头部中提取第一个 IPv4 地址"""
    for header in reversed(received_headers):  # 最早的一跳在最后面
        match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', header)
        if match:
            return match.group(0)
    return None

def parse_email(file_path):
    """解析单封邮件，结构化为字典"""
    try:
        with open(file_path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)

        # 收件人字段
        raw_from = msg.get("From", "")
        raw_to = msg.get_all("To", [])
        raw_subject = msg.get("Subject", "")
        raw_date = msg.get("Date", "")
        received_headers = msg.get_all("Received", [])

        # 邮箱提取
        sender = parseaddr(raw_from)[1].strip().lower()
        receivers = [addr.strip().lower() for name, addr in getaddresses(raw_to) if addr]

        # IP 提取
        ip_address = extract_ip_from_headers(received_headers)

        # 构造输出结构
        parsed = {
            "file": os.path.basename(file_path),
            "sender": sender,
            "receivers": receivers,
            "subject": raw_subject,
            "date": raw_date,
            "ip": ip_address,
            "body_text": "",
            "body_html": "",
            "attachments": [],
            "attachment_types": [],
        }

        # 遍历各部分
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = part.get_content_disposition()

            if content_type == "text/plain" and not parsed["body_text"]:
                try:
                    parsed["body_text"] = part.get_content()
                except:
                    pass

            elif content_type == "text/html" and not parsed["body_html"]:
                try:
                    parsed["body_html"] = part.get_content()
                except:
                    pass

            elif content_disposition == "attachment":
                filename = part.get_filename()
                if filename:
                    parsed["attachments"].append(filename)
                    parsed["attachment_types"].append(content_type.lower())

        return parsed

    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}")
        return {
            "file": os.path.basename(file_path),
            "error": str(e),
            "sender": "",
            "receivers": [],
            "subject": "",
            "date": "",
            "ip": None,
            "body_text": "",
            "body_html": "",
            "attachments": [],
            "attachment_types": [],
        }

def parse_all_emails():
    all_emails = []
    count = 0

    for root, _, files in os.walk(MAIL_DIR):
        for file in files:
            if file.lower().endswith(".eml"):
                file_path = os.path.join(root, file)
                parsed = parse_email(file_path)
                all_emails.append(parsed)
                count += 1

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_emails, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Parsed {count} emails → {OUTPUT_JSON}")

if __name__ == "__main__":
    parse_all_emails()
