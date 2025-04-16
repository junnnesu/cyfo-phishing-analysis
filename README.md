# CYFO INC Spear Phishing Analysis Project

This repository contains a full forensic analysis pipeline for detecting and visualizing spear phishing emails targeting a fictional organization, CYFO INC.

---

## 📁 Project Structure

```bash
cyfo-forensics/
├── parser.py              # EML parser to extract structured fields
├── clean.py               # Data cleaning and normalization
├── analyze.py             # SQL-like querying using pandas/sqlite
├── spear_analysis.py      # Target detection and IP whois attribution
├── visualize.py           # Email trend and attachment visualizations
├── employees.csv          # Sample employee directory (name, email, dept)
├── parser_output.json     # Structured email data (raw)
├── cleaned_emails.json    # Cleaned email data
├── requirements.txt       # Python dependencies
├── output/
│   ├── spear_department_bar.png
│   ├── attacker_orgs.png
│   ├── attacker_countries.png
│   ├── spear_report.md
├── spear_report_zh.html   # Chinese full HTML report
├── spear_report_en.html   # English full HTML report
```

---

## 🚀 How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Parse emails
```bash
python parser.py
```

### 3. Clean extracted data
```bash
python clean.py
```

### 4. Run SQL-like analysis
```bash
python analyze.py
```

### 5. Spear phishing detection + attribution
```bash
python spear_analysis.py
```

### 6. Optional: Generate visualizations
```bash
python visualize.py
```

---

## 📊 Output Samples

- Targeted department chart

  ![Department Chart](output/spear_department_bar.png)

- Attacker organizations

  ![Organizations](output/attacker_orgs.png)

- Attacker country distribution

  ![Countries](output/attacker_countries.png)

---

## 📑 Report
- [spear_report_en.html](./spear_report_en.html) — English PDF/printable report

---

## 🛡 License & Disclaimer
This is a fictional forensic project for educational and research purposes only. All data has been anonymized or generated for simulation.
