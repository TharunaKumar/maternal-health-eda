import re
import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator
import matplotlib.pyplot as plt
import seaborn as sns


# ── Load & Prepare Data ───────────────────────────────────────────────────────
df = pd.read_excel(r"/Users/tharunakumar/Desktop/Maternal_DS.xlsx", header=1, na_values=[], keep_default_na=False)

def translate_and_clean(text):
    if pd.isna(text):
        return text
    translated = GoogleTranslator(source="auto", target="en").translate(str(text))
    cleaned = translated.lower().strip()
    cleaned = re.sub(r"[\s\-]+", "_", cleaned)
    cleaned = re.sub(r"[^\w]", "", cleaned)
    return cleaned

df.columns = [translate_and_clean(col) for col in df.columns]

# Fill NaN with 'None' for all string/object columns
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].fillna('None')

# Parse blood pressure & compute MAP
df[['systolic_bp', 'diastolic_bp']] = df['blood_pressure'].str.split('/', expand=True)
df['systolic_bp'] = pd.to_numeric(df['systolic_bp'], errors='coerce')
df['diastolic_bp'] = pd.to_numeric(df['diastolic_bp'], errors='coerce')
df['mean_arterial_pressure'] = (df['systolic_bp'] + (2 * df['diastolic_bp'])) / 3

# Parse weight and height, compute BMI
df['weight_kg'] = df['weight'].str.extract(r'(\d+\.?\d*)').astype(float)
df['height_ft'] = df['height'].str.extract(r'(\d+\.?\d*)').astype(float)
df['height_m'] = df['height_ft'] * 0.3048
df['bmi'] = df['weight_kg'] / (df['height_m'] ** 2)

def bmi_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

df['bmi_category'] = df['bmi'].apply(bmi_category)

print("BMI stats:")
print(df['bmi'].describe().round(2))
print("\nBMI category counts:")
print(df['bmi_category'].value_counts())

# ── Plots ─────────────────────────────────────────────────────────────────────
GREEN, RED, ORANGE, BLUE = '#2ecc71', '#e74c3c', '#f39c12', '#3498db'
sns.set_theme(style='whitegrid', font_scale=1.05)

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.subplots_adjust(hspace=0.45, wspace=0.35)

# Plot 1: BMI Distribution by risk group
ax1 = axes[0, 0]
for risk, color, label in [('No', GREEN, 'Not Risky'), ('Yes', RED, 'Risky')]:
    subset = df[df['risky_pregnancy'] == risk]['bmi']
    ax1.hist(subset, bins=20, alpha=0.5, color=color, label=label, edgecolor='white')
ax1.axvline(18.5, color='gray', linestyle='--', linewidth=1, label='Underweight (<18.5)')
ax1.axvline(25.0, color='black', linestyle='--', linewidth=1, label='Overweight (>25)')
ax1.set_title('BMI Distribution\nby Risk Group', fontsize=13, fontweight='bold')
ax1.set_xlabel('BMI')
ax1.set_ylabel('Count')
ax1.legend(fontsize=8)

# Plot 2: BMI vs MAP scatter coloured by risk
ax2 = axes[0, 1]
for risk, color, label in [('No', GREEN, 'Not Risky'), ('Yes', RED, 'Risky')]:
    subset = df[df['risky_pregnancy'] == risk]
    ax2.scatter(subset['bmi'], subset['mean_arterial_pressure'],
                alpha=0.4, s=20, color=color, label=label)
ax2.set_title('BMI vs MAP\nby Risk Group', fontsize=13, fontweight='bold')
ax2.set_xlabel('BMI')
ax2.set_ylabel('Mean Arterial Pressure (mmHg)')
ax2.legend(fontsize=9)

# Plot 3: Weight distribution by risk group
ax3 = axes[1, 0]
sns.boxplot(data=df, x='risky_pregnancy', y='weight_kg',
            hue='risky_pregnancy', palette={'No': GREEN, 'Yes': RED},
            legend=False, ax=ax3)
ax3.set_title('Weight Distribution\nby Risk Group', fontsize=13, fontweight='bold')
ax3.set_xlabel('Pregnancy Risk Level')
ax3.set_ylabel('Weight (kg)')

# Plot 4: Age vs BMI scatter coloured by risk
ax4 = axes[1, 1]
for risk, color, label in [('No', GREEN, 'Not Risky'), ('Yes', RED, 'Risky')]:
    subset = df[df['risky_pregnancy'] == risk]
    ax4.scatter(subset['age'], subset['bmi'],
                alpha=0.4, s=20, color=color, label=label)
ax4.set_title('Age vs BMI\nby Risk Group', fontsize=13, fontweight='bold')
ax4.set_xlabel('Age')
ax4.set_ylabel('BMI')
ax4.legend(fontsize=9)

fig.suptitle('Weight & BMI Analysis — Maternal Health Dataset',
             fontsize=16, fontweight='bold', y=1.01)

plt.tight_layout()
plt.savefig('bmi_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved as bmi_analysis.png")