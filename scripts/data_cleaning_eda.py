# =============================================================================
# Maternal Health EDA — Data Cleaning & Initial Analysis
# =============================================================================
# This script handles:
#   1. Loading the raw Bengali dataset
#   2. Translating column names to English
#   3. Parsing blood pressure and computing Mean Arterial Pressure (MAP)
#   4. Extracting numerical gravida from ordinal strings (e.g. "1st" -> 1)
#   5. Summarising missing values, clinical averages, and age distribution
#   6. Plotting MAP distribution and anemia severity by risk group
# =============================================================================

import re
import pandas as pd
from deep_translator import GoogleTranslator
import matplotlib.pyplot as plt
import seaborn as sns


# ── 1. Load Dataset ───────────────────────────────────────────────────────────
# header=1 skips the first row since the actual column names are on row 2
# na_values=[] and keep_default_na=False prevent pandas from auto-converting
# values like "None" or empty strings into NaN
df = pd.read_excel(
    r"/Users/tharunakumar/Desktop/Maternal_DS.xlsx",
    header=1,
    na_values=[],
    keep_default_na=False
)


# ── 2. Translate Column Names ─────────────────────────────────────────────────
# Column names are in Bengali so we auto-translate them to English using
# Google Translate, then clean the result 
def translate_and_clean(text):
    if pd.isna(text):
        return text

    # Translate Bengali text to English
    translated = GoogleTranslator(source="auto", target="en").translate(str(text))

    # Convert to lowercase snake_case and remove punctuation
    cleaned = translated.lower().strip()
    cleaned = re.sub(r"[\s\-]+", "_", cleaned)   # spaces/hyphens → underscores
    cleaned = re.sub(r"[^\w]", "", cleaned)       # remove any remaining punctuation

    return cleaned

df.columns = [translate_and_clean(col) for col in df.columns]


# ── 3. Check for Missing Values ───────────────────────────────────────────────
print("\nMissing values per feature:")
print(df.isnull().sum())


# ── 4. Parse Blood Pressure & Compute MAP ────────────────────────────────────
# Blood pressure is stored as a string e.g. "120/80"
# We split it into two separate numeric columns: systolic and diastolic
df[['systolic_bp', 'diastolic_bp']] = df['blood_pressure'].str.split('/', expand=True)
df['systolic_bp'] = pd.to_numeric(df['systolic_bp'], errors='coerce')
df['diastolic_bp'] = pd.to_numeric(df['diastolic_bp'], errors='coerce')

# Save the cleaned dataframe to CSV for use in other scripts
df.to_csv('maternal_health_clean.csv', index=False)

# Mean Arterial Pressure (MAP) is a clinical measure of average blood pressure
# Formula: (Systolic + 2 × Diastolic) / 3
df['mean_arterial_pressure'] = (df['systolic_bp'] + (2 * df['diastolic_bp'])) / 3


# ── 5. Extract Numerical Gravida ──────────────────────────────────────────────
# The 'pregnant' column stores values like "1st", "2nd", "3rd"
# We extract just the number so we can use it in calculations
df['gravida_numerical'] = df['pregnant'].str.extract(r'(\d+)').astype(float)
df['gravida_numerical'] = df['gravida_numerical'].fillna(1).astype(int)

# Preview the parsed blood pressure and MAP columns
print(df[['name', 'blood_pressure', 'systolic_bp', 'diastolic_bp',
          'mean_arterial_pressure', 'gravida_numerical']].head())


# ── 6. Risk Group Analysis ────────────────────────────────────────────────────
# Compare average clinical metrics between risky and non-risky pregnancies
risk_analysis = df.groupby('risky_pregnancy')[
    ['age', 'systolic_bp', 'diastolic_bp', 'mean_arterial_pressure', 'gravida_numerical']
].mean()
print("\nAverage Clinical Metrics by Pregnancy Risk Level:")
print(risk_analysis)

# Break down the age range within each risk group
age_distribution = df.groupby('risky_pregnancy')['age'].agg(['min', 'median', 'max'])
print("\nAge Distribution Breakdown:")
print(age_distribution)


# ── 7. Plots ──────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid")
plt.figure(figsize=(14, 6))

# Plot 1: Boxplot — MAP by risk group
# Shows whether higher blood pressure correlates with risky pregnancies
plt.subplot(1, 2, 1)
sns.boxplot(
    data=df,
    x='risky_pregnancy',
    y='mean_arterial_pressure',
    hue='risky_pregnancy',
    palette={'No': '#2ecc71', 'Yes': '#e74c3c'},  # green = safe, red = risky
    legend=False
)
plt.title('Distribution of Mean Arterial Pressure (MAP)', fontsize=14, pad=15)
plt.xlabel('Pregnancy Risk Level', fontsize=12)
plt.ylabel('MAP (mmHg)', fontsize=12)

# Plot 2: Countplot — Anemia severity broken down by risk group
# Shows whether more severe anemia is associated with higher risk
plt.subplot(1, 2, 2)
anemia_order = [v for v in ['None', 'Minimal', 'Medium', 'High'] if v in df['anemia'].unique()]
sns.countplot(
    data=df,
    x='anemia',
    hue='risky_pregnancy',
    order=anemia_order,
    palette={'No': '#2ecc71', 'Yes': '#e74c3c'}
)
plt.title('Anemia Severity vs Pregnancy Risk', fontsize=14, pad=15)
plt.xlabel('Anemia Category', fontsize=12)
plt.ylabel('Number of Patients', fontsize=12)
plt.legend(title='Risky Pregnancy')

plt.tight_layout()
plt.savefig('data_cleaning_eda.png', dpi=150, bbox_inches='tight')
plt.show()