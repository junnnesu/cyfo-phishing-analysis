import pandas as pd
import json
import matplotlib.pyplot as plt
import os
from collections import Counter
from datetime import datetime
from ipwhois import IPWhois
from tqdm import tqdm

EMAIL_FILE = "cleaned_emails.json"
EMPLOYEE_CSV = "employees.csv"
OUTPUT_DIR = "output"
REPORT_FILE = os.path.join(OUTPUT_DIR, "spear_report.md")

def load_data():
    with open(EMAIL_FILE, "r", encoding="utf-8") as f:
        emails = json.load(f)
    employees = pd.read_csv(EMPLOYEE_CSV)
    employees["email"] = employees["email"].str.strip().str.lower()
    employees["department"] = employees["department"].str.strip()
    return emails, employees

def find_targets(emails, employee_emails):
    spear_rows = []
    for e in emails:
        for r in e.get("receivers", []):
            r_clean = r.strip().lower()
            if r_clean in employee_emails:
                spear_rows.append({
                    "file": e["file"],
                    "date": e.get("clean_date"),
                    "receiver": r_clean,
                    "ip": e.get("ip")
                })
    return pd.DataFrame(spear_rows)

def plot_department_bar(target_df, employee_df):
    merged = target_df.merge(employee_df, left_on="receiver", right_on="email")
    dept_counts = merged["department"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 5))
    dept_counts.plot(kind='bar', ax=ax)
    ax.set_title("Spear Phishing Emails per Department")
    ax.set_xlabel("Department")
    ax.set_ylabel("Email Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, "spear_department_bar.png")
    fig.savefig(output_path)
    plt.close(fig)
    print(f"✅ Saved department chart to {output_path}")
    return f"### Targeted Departments\n![Department Chart]({os.path.basename(output_path)})"

import ipaddress

def is_public_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_global
    except:
        return False

def analyze_attacker_ips(target_df):
    print("🌍 Running WHOIS lookup for attacker IPs...")

    country_counter = Counter()
    org_counter = Counter()
    skipped = []

    # 🔍 仅保留公网 IP
    unique_ips = [ip for ip in target_df["ip"].dropna().unique() if is_public_ip(ip)]

    if not unique_ips:
        print("⚠️ No public IPs found for WHOIS.")
        return ["### Attacker Organizations\n_No public IPs available_",
                "### Attacker Country Distribution\n_No public IPs available_"]

    for ip in tqdm(unique_ips):
        try:
            obj = IPWhois(ip)
            res = obj.lookup_rdap()
            country = res.get("network", {}).get("country")
            if not country:
                country = res.get("asn_country_code", "Unknown")
            org = res.get("network", {}).get("name", "Unknown")
            print(f"{ip} → {country}, {org}")
            country_counter[country] += 1
            org_counter[org] += 1
        except Exception:
            skipped.append(ip)
            country_counter["Unknown"] += 1

    # 组织图
    if org_counter:
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        labels, values = zip(*org_counter.most_common(10))
        wedges, texts, autotexts = ax1.pie(values, labels=None, autopct='%1.1f%%', startangle=140)
        ax1.legend(wedges, labels, title="Organizations", loc="center left", bbox_to_anchor=(1, 0.5))
        ax1.set_title("Top Attacker Organizations")
        org_path = os.path.join(OUTPUT_DIR, "attacker_orgs.png")
        fig1.savefig(org_path, bbox_inches="tight")
        plt.close(fig1)
        org_md = f"### Attacker Organizations\n![Attacker Organizations]({os.path.basename(org_path)})"
    else:
        org_md = "### Attacker Organizations\n_No data available_"

    # 国家图
    if country_counter:
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        labels2, values2 = zip(*country_counter.most_common(10))
        wedges2, texts2, autotexts2 = ax2.pie(values2, labels=None, autopct='%1.1f%%', startangle=140)
        ax2.legend(wedges2, labels2, title="Countries", loc="center left", bbox_to_anchor=(1, 0.5))
        ax2.set_title("Attacker Country Distribution")
        country_path = os.path.join(OUTPUT_DIR, "attacker_countries.png")
        fig2.savefig(country_path, bbox_inches="tight")
        plt.close(fig2)
        country_md = f"### Attacker Country Distribution\n![Attacker Country Distribution]({os.path.basename(country_path)})"
    else:
        country_md = "### Attacker Country Distribution\n_No data available_"

    # 可选输出跳过的 IP
    if skipped:
        print("⚠️ Skipped due to WHOIS errors:", skipped)

    return [org_md, country_md]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    emails, employees = load_data()
    employee_emails = set(employees["email"])
    target_df = find_targets(emails, employee_emails)

    print(f"🎯 Spear phishing emails targeting CYFO INC employees: {len(target_df)}")

    md_lines = [
        "# 🎯 CYFO INC – Spear Phishing Analysis",
        f"Report generated: {datetime.utcnow().isoformat()} UTC",
        f"Total spear phishing emails: **{len(target_df)}**",
        f"Unique employees targeted: **{target_df['receiver'].nunique()}**"
    ]

    md_lines.append(plot_department_bar(target_df, employees))
    md_lines += analyze_attacker_ips(target_df)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n\n".join(md_lines))

    print(f"\n📄 Markdown report saved to {REPORT_FILE}")

if __name__ == "__main__":
    main()
