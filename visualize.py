import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import os
from datetime import datetime
import matplotlib

# Set font to avoid issues with non-Latin characters
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

INPUT_FILE = "cleaned_emails.json"
OUTPUT_DIR = "output"
MARKDOWN_FILE = os.path.join(OUTPUT_DIR, "report.md")

def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_plot(fig, filename, title):
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, bbox_inches="tight")
    print(f"✅ Saved: {path}")
    return f"### {title}\n![{title}]({filename})\n"

def plot_email_trend(df):
    print("📈 Plotting: Email Volume Over Time...")
    df['clean_date'] = pd.to_datetime(df['clean_date'], errors='coerce')
    df = df.dropna(subset=["clean_date"])
    df['date_only'] = df['clean_date'].dt.date
    trend = df.groupby("date_only").size()

    fig, ax = plt.subplots(figsize=(10, 5))
    trend.plot(kind='line', marker='o', ax=ax)
    ax.set_title("Email Volume Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Email Count")
    ax.grid(True)
    plt.tight_layout()
    return save_plot(fig, "email_trend.png", "Email Volume Over Time")

def plot_top_senders(df, top_n=10):
    print("📊 Plotting: Top Senders...")
    top_senders = df['sender'].value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(10, 5))
    top_senders.plot(kind='bar', ax=ax)
    ax.set_title(f"Top {top_n} Senders by Email Count")
    ax.set_xlabel("Sender")
    ax.set_ylabel("Email Count")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return save_plot(fig, "top_senders.png", f"Top {top_n} Senders by Email Count")

def plot_attachment_distribution(df):
    print("🥧 Plotting: Attachment Type Distribution...")
    types = []
    for email in df.itertuples():
        if isinstance(email.attachment_types, list):
            types.extend(email.attachment_types)

    counter = Counter(types)
    if not counter:
        return ""

    labels, values = zip(*counter.items())
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.set_title("Attachment Type Distribution")
    plt.tight_layout()
    return save_plot(fig, "attachment_distribution.png", "Attachment Type Distribution")

def main():
    ensure_output_dir()
    data = load_data()
    df = pd.DataFrame(data)
    df["sender"] = df["sender"].fillna("").astype(str)
    df["attachment_types"] = df["attachment_types"].apply(lambda x: x if isinstance(x, list) else [])

    md_sections = []
    md_sections.append("# 📊 Email Analysis Report")
    md_sections.append(f"Generated on: {datetime.utcnow().isoformat()} UTC\n")

    md_sections.append(plot_email_trend(df))
    md_sections.append(plot_top_senders(df))
    md_sections.append(plot_attachment_distribution(df))

    with open(MARKDOWN_FILE, "w", encoding="utf-8") as f:
        f.write("\n\n".join(md_sections))

    print(f"\n📄 Markdown report generated: {MARKDOWN_FILE}")

if __name__ == "__main__":
    main()
