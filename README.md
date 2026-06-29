# Maternal Health EDA

Exploratory Data Analysis on a maternal health dataset originally recorded in Bengali. This project covers data cleaning, translation, feature engineering, and multiple analysis tracks to identify risk factors in pregnancy.

---

## Dataset

- **File:** `Maternal_DS.xlsx`
- **Rows:** 998 patients
- **Language:** Column names in Bengali — automatically translated to English using `deep_translator`
- **Target variable:** `risky_pregnancy` (Yes / No)

**Features include:** age, weight, height, blood pressure, gestational age, gravida, anemia, jaundice, fetal position, fetal heartbeat, urine albumin & sugar, VDRL, HRsAG

---

## Project Structure

```
├── data/
│   └── Maternal_DS.xlsx
├── scripts/
│   ├── test.py                   # Data loading, cleaning, MAP calculation, initial plots
│   ├── risk_factor_analysis.py   # Risk factor deep-dive (anemia, BP, jaundice, fetal position)
│   ├── correlation_analysis.py   # Correlation heatmap and pairplot
│   └── BMI_analysis.py           # Weight and BMI analysis
├── outputs/
│   ├── risk_factor_analysis.png
│   ├── correlation_heatmap.png
│   ├── pairplot.png
│   └── bmi_analysis.png
├── requirements.txt
└── README.md
```

---

## Analyses

### 1. Data Cleaning & Initial EDA (`test.py`)
- Translates Bengali column names to English using Google Translate via `deep_translator`
- Parses blood pressure strings (e.g. `"120/80"`) into systolic and diastolic components
- Computes **Mean Arterial Pressure (MAP)**: `(Systolic + 2 × Diastolic) / 3`
- Extracts numerical gravida from ordinal strings (e.g. `"1st"` → `1`)
- Plots MAP distribution and anemia severity by risk group

### 2. Risk Factor Deep-Dive (`risk_factor_analysis.py`)
- Analyses co-occurrence of anemia and high BP with risky pregnancy
- Evaluates VDRL, HRsAG, jaundice severity, and fetal position as risk indicators
- **Key finding:** Any patient with high BP (systolic ≥ 120) is classified as risky 100% of the time — the strongest single predictor in the dataset

### 3. Correlation & Multivariate Analysis (`correlation_analysis.py`)
- Correlation heatmap across all numerical clinical features
- Pairplot coloured by risk group to spot multivariate separation
- **Key finding:** BP-related features (systolic, diastolic, MAP) show the clearest separation between risk groups; weight, height, and gestational age show near-zero correlation with risk

### 4. Weight & BMI Analysis (`BMI_analysis.py`)
- Parses weight (kg) and height (ft), converts height to metres, computes BMI
- Classifies patients into WHO BMI categories (Underweight / Normal / Overweight)
- **Key finding:** BMI alone is not a strong predictor of pregnancy risk in this cohort — distributions are nearly identical across risk groups

---

## Key Findings Summary

| Factor | Finding |
|---|---|
| High BP | 100% of high-BP patients classified as risky — strongest predictor |
| HRsAG | Positive results appear exclusively in the risky group (16.4%) |
| VDRL | No predictive value — 50/50 split in both risk groups |
| Anemia | Not a standalone predictor; risk % similar across severity levels |
| BMI / Weight | No meaningful separation between risk groups |
| Age | Similar distribution across risk groups — not a strong standalone predictor |

---

## Setup & Usage

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run any script:**
```bash
python scripts/test.py
python scripts/risk_factor_analysis.py
python scripts/correlation_analysis.py
python scripts/BMI_analysis.py
```

> **Note:** Update the `pd.read_excel(...)` path in each script to point to your local copy of `Maternal_DS.xlsx`, or place the file in the same directory as the script and use just the filename.

---

## Requirements

- Python 3.8+
- pandas, numpy, matplotlib, seaborn, openpyxl, deep-translator