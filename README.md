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

## Analysis

### 1. Data Cleaning & Initial EDA (`data_cleaning_eda.py`)
#### Data Cleaning Steps
The raw dataset presented two key challenges before any analysis could begin:

##### Language barrier
All column names were in Bengali. Rather than renaming them manually, deep_translator was used to automatically translate each column name to English via Google Translate, then convert the result to snake_case for clean programmatic access.
##### Unstructured fields
Blood pressure was recorded as "120/80", weight as "50 kg", height as "5.2''", and gravida as "1st" or "2nd". 
No missing values were found across all 998 rows and 18 columns.
#### Feature Engineering
Calculated two new clinical features from the raw data:

##### Mean Arterial Pressure (MAP)
Calculated using the standard formula: MAP = (Systolic + 2 × Diastolic) / 3. MAP is a more stable measure of perfusion pressure than systolic BP alone and is widely used in obstetric risk assessment.
##### Numerical Gravida
Extracted from ordinal strings (e.g. "1st" → 1) using regex, enabling gravida to be used as a numerical feature in grouping and correlation analyses.

#### Visualisations
##### Plot 1 : Distribution of Mean Arterial Pressure (MAP) by Risk Group
The boxplot shows an upward shift in MAP for the risky pregnancy group compared to the non-risky group:

The risky group has a median MAP of approximately 77 mmHg, with an IQR between ~74–80 mmHg and a narrow overall spread.
The non-risky group has a lower median MAP of approximately 73 mmHg, a wider IQR (~70–80 mmHg), indicating greater variability among lower-risk patients.
The tighter, higher distribution in the risky group suggests that elevated MAP is a consistent characteristic of risky pregnancies.

##### Plot 2 : Anemia Severity vs Pregnancy Risk
The countplot breaks down anemia status across both risk groups:

The majority of patients fall into the None category (~580 risky, ~290 non-risky), which shows an overall 2:1 class imbalance in the dataset.
For both Minimal and Medium anemia categories, the ~2:1 risky-to-non-risky ratio is still there, with roughly 45 risky vs 20 non-risky patients in each.
The consistent ratio across all anemia categories suggests that anemia severity alone does not meaningfully increase pregnancy risk beyond the baseline rate.
### 2. Risk Factor Analysis (`risk_factor_analysis.py`)
#### Overview
This analysis investigates how individual and combined clinical risk factors relate to pregnancy risk classification. Five plots examine blood pressure, anemia, MAP, jaundice, and fetal position as potential indicators of risk.

#### Visualisations
##### Plot 1 : Anemia and High BP vs Risky Pregnancy %
This plot examines whether the combination of anemia and high BP (systolic ≥ 120) drives risk classification more than either factor alone:

Patients with no anemia and normal BP have a 63.7% risk rate where the baseline in the dataset is 66.6%.
Patients with anemia and normal BP show a similar 64.3% risk rate, indicating that anemia alone does not contribute a risky pregnancy.
Both groups with high BP — regardless of whether anemia is present — are classified as risky 100% of the time, making high blood pressure the single strongest predictor in the entire dataset.

##### Plot 2 : Risk % by Anemia Severity

Across all three anemia categories — None (66.7%), Minimal (66.1%), and Medium (67.2%) — the risk percentage stays within 1% of each other
This near-flat pattern shows that anemia severity has no meaningful independent effect on pregnancy risk classification.

##### Plot 3 : Distribution of MAP by Risk Group
The boxplot shows an upward shift in MAP for the risky pregnancy group compared to the non-risky group:

The risky group has a median MAP of approximately 77 mmHg, with an IQR between ~74–80 mmHg and a narrow overall spread.
The non-risky group has a lower median MAP of approximately 73 mmHg, a wider IQR (~70–80 mmHg), indicating greater variability among lower-risk patients.
The tighter, higher distribution in the risky group suggests that elevated MAP is a consistent characteristic of risky pregnancies.

##### Plot 4 : 

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
