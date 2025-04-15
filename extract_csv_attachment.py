import os
import email
from email import policy
from email.parser import BytesParser

MAIL_DIR = "/forensics/cyfo-forensics/spam_emails"
OUTPUT_DIR = "attachments"

os.makedirs(OUTPUT_DIR, exist_ok=True)

count = 0
for root, _, files in os.walk(MAIL_DIR):
    for file in files:
        if not file.lower().endswith(".eml"):
            continue
        path = os.path.join(root, file)

        try:
            with open(path, "rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)

            for part in msg.walk():
                if part.get_content_disposition() == "attachment":
                    filename = part.get_filename()
                    if filename and filename.lower().endswith(".csv"):
                        output_name = f"{os.path.splitext(file)[0]}__{filename}"
                        output_path = os.path.join(OUTPUT_DIR, output_name)
                        with open(output_path, "wb") as out:
                            out.write(part.get_payload(decode=True))
                        print(f"✅ Extracted: {output_path}")
                        count += 1
        except Exception as e:
            print(f"❌ Error parsing {file}: {e}")

print(f"\n✅ 共提取 {count} 个 .csv 附件，保存在 {OUTPUT_DIR}/")
