import json
import sqlite3
import pandas as pd
import re
from collections import Counter

INPUT_JSON = "cleaned_emails.json"

def load_data():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def prepare_sql_safe_dataframe(df):
    for col in df.columns:
        df[col] = df[col].apply(lambda x:
            ",".join(x) if isinstance(x, list)
            else str(x) if x is not None and not isinstance(x, (int, float, bool))
            else x
        )
    return df

def analyze(emails):
    # 主表
    email_df = pd.DataFrame(emails)
    email_df = email_df[email_df["file"].notnull()].drop_duplicates(subset="file")

    # 展开收件人（用于其它分析）
    receiver_rows = []
    for e in emails:
        for r in e.get("receivers", []):
            if r:
                receiver_rows.append({"file": e["file"], "receiver": r})
    receivers_df = pd.DataFrame(receiver_rows).dropna().drop_duplicates()

    # 展开附件
    attachment_rows = []
    for e in emails:
        for t in e.get("attachment_types", []):
            if t:
                attachment_rows.append({"file": e["file"], "type": t.lower()})
    attachments_df = pd.DataFrame(attachment_rows)

    # 预处理字段以防 SQLite 报错
    email_df = prepare_sql_safe_dataframe(email_df)

    # 建立 SQLite 数据库
    conn = sqlite3.connect(":memory:")
    email_df.to_sql("emails", conn, index=False, if_exists="replace")
    receivers_df.to_sql("receivers", conn, index=False, if_exists="replace")
    attachments_df.to_sql("attachments", conn, index=False, if_exists="replace")

    # SQL 查询
    queries = {
        "Q1: Total emails": "SELECT COUNT(*) FROM emails",
        "Q2: Unique senders": "SELECT COUNT(DISTINCT sender) FROM emails WHERE sender != ''",
        "Q4: Earliest email date (UTC)": "SELECT MIN(clean_date) FROM emails WHERE clean_date IS NOT NULL",
        "Q5: Latest email date (UTC)": "SELECT MAX(clean_date) FROM emails WHERE clean_date IS NOT NULL",
        "Q8: Total attachments": "SELECT COUNT(*) FROM attachments",
        "Q9: PDF attachments": "SELECT COUNT(*) FROM attachments WHERE type = 'application/pdf'",
        "Q10: JPEG or PNG attachments": """
            SELECT COUNT(*) FROM attachments
            WHERE type IN ('image/jpeg', 'image/jpg', 'image/png')
        """
    }

    print("\n📊 Analysis Results:\n")
    for label, sql in queries.items():
        try:
            result = conn.execute(sql).fetchone()[0]
            print(f"{label}: {result}")
        except Exception as e:
            print(f"{label}: Error - {e}")

    # ✅ Q3: Unique receivers (only To)
    unique_receivers = set()
    for e in emails:
        for r in e.get("receivers", []):
            if isinstance(r, str):
                r = r.strip().lower()
                if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", r):
                    unique_receivers.add(r)
    print(f"Q3: Unique receivers (To only): {len(unique_receivers)}")

    # Q6-Q7: Word frequency
    print("\n🧠 Word Frequency (plain text bodies):")

    all_text = " ".join(email_df["body_text"].dropna()).lower()
    words = re.findall(r'\b[a-z]{2,}\b', all_text)
    counter = Counter(words)
    top_words = counter.most_common(2)

    if len(top_words) >= 2:
        print(f"Q6: Most popular word: '{top_words[0][0]}' ({top_words[0][1]} times)")
        print(f"Q7: 2nd most popular word: '{top_words[1][0]}' ({top_words[1][1]} times)")
    else:
        print("Q6/Q7: Not enough words found.")

if __name__ == "__main__":
    emails = load_data()
    analyze(emails)
