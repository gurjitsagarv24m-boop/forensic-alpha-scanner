Here is a **clean, professional, submission-ready `README.md`** you can copy-paste directly into GitHub.

---

```markdown
# 🔍 Forensic Alpha Scanner

A **forensic accounting–driven investment analysis tool** that computes multi-year forensic scores and a composite **Forensic Alpha** to generate **Long / Short / Hold** recommendations.

Built as a Streamlit web application for academic, research, and applied finance use.

---

## 🚀 What This Project Does

The Forensic Alpha Scanner:
- Ingests **multi-year financial statements** (CSV / Excel)
- Normalizes line items into canonical financial variables
- Computes **key forensic accounting scores**
- Aggregates them into a **Forensic Alpha**
- Produces a **quantitative investment signal**
- Optionally adds **AI-assisted qualitative reasoning**

---

## 🧠 Forensic Scores Implemented

The application calculates the following (year-wise):

| Score | Purpose |
|-----|------|
| **Beneish M-Score** | Earnings manipulation risk |
| **Sloan Accrual Ratio** | Earnings quality |
| **Piotroski F-Score** | Fundamental strength |
| **Altman Z-Score** | Bankruptcy risk |
| **Forensic Alpha (Composite)** | Investment signal |

> **Note:** Alpha is derived from normalized and direction-aware transformations of the above metrics.

---

## 📊 Forensic Alpha Logic

Forensic Alpha is computed using:

- Z-score normalization across time
- Direction-aware signals:
  - Higher Beneish → worse
  - Higher Sloan → worse
  - Higher Piotroski → better
  - Higher Altman → safer
- Weighted aggregation:

```

Forensic Alpha =
0.35 × Beneish
0.25 × Sloan
0.25 × Piotroski
0.15 × Altman

```

### Interpretation
| Alpha Value | Signal |
|-----------|-------|
| > 1.0 | Strong Long |
| 0.3 – 1.0 | Long |
| −0.3 – 0.3 | Hold |
| −1.0 – −0.3 | Short |
| < −1.0 | Strong Short |
---

## 📥 Input Format (Required)

Upload **CSV or Excel** with the following structure:

| Statement | Item | 2022 | 2023 | 2024 |
|---------|------|------|------|------|
| Income Statement | Revenue | 1000000 | 1200000 | 1400000 |
| Balance Sheet | Total Assets | 1500000 | 1700000 | 1900000 |
| Cash Flow | Operating Cash Flow | 180000 | 210000 | 250000 |

- Supports **any number of years**
- Missing values are handled safely
- Line items are mapped to canonical names internally

---

## ▶️ How to Run the App

### 1️⃣ Install Dependencies
```bash
pip install streamlit pandas numpy
````

### 2️⃣ Run Streamlit

```bash
streamlit run app.py
```

### 3️⃣ Open Browser

```
http://localhost:8501
```

---

## 🧪 Outputs

* Editable normalized financial table
* Year-wise forensic score tables
* Composite forensic alpha time series
* Investment recommendation:

  * **Long**
  * **Short**
  * **Hold**

---

## 🎯 Intended Use

* MBA / Finance coursework
* Forensic accounting research
* Investment screening models
* Case competitions
* Applied financial analytics demos

---

## ⚠️ Disclaimer

This project is for **educational and analytical purposes only**.
It is **not investment advice**.

---

## 👤 Author

**Gurjit Sagarv**
MBA | Finance | Forensic Accounting
IIM Ranchi
