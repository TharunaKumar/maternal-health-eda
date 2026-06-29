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

# Parse weight, height, gestational age into numbers
df['weight_kg'] = df['weight'].str.extract(r'(\d+\.?\d*)').astype(float)
df['height_ft'] = df['height'].str.extract(r'(\d+\.?\d*)').astype(float)
df['gestational_weeks'] = df['pregnancy'].str.extract(r'(\d+)').astype(float)

# Extract numerical gravida
df['gravida_numerical'] = df['pregnant'].str.extract(r'(\d+)').astype(float)
df['gravida_numerical'] = df['gravida_numerical'].fillna(1).astype(int)

# ── Numerical feature set ─────────────────────────────────────────────────────
num_cols = ['age', 'weight_kg', 'height_ft', 'gestational_weeks',
            'systolic_bp', 'diastolic_bp', 'mean_arterial_pressure', 'gravida_numerical']
num_df = df[num_cols]

print("Correlation Matrix:")
print(num_df.corr().round(2))

# ── Figure 1: Correlation Heatmap ─────────────────────────────────────────────
sns.set_theme(style='whitegrid', font_scale=1.1)

fig, ax = plt.subplots(figsize=(10, 8))
corr = num_df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))  # hide upper triangle

sns.heatmap(
    corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
    vmin=-1, vmax=1, center=0, linewidths=0.5,
    annot_kws={'size': 11}, ax=ax
)
ax.set_title('Correlation Heatmap — Clinical Features', fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
print("Heatmap saved as correlation_heatmap.png")

# ── Figure 2: Pairplot ────────────────────────────────────────────────────────
pair_cols = ['age', 'weight_kg', 'systolic_bp', 'diastolic_bp',
             'mean_arterial_pressure', 'gravida_numerical']
pair_df = df[pair_cols + ['risky_pregnancy']].copy()

g = sns.pairplot(
    pair_df,
    hue='risky_pregnancy',
    palette={'No': '#2ecc71', 'Yes': '#e74c3c'},
    plot_kws={'alpha': 0.5, 's': 20},
    diag_kind='kde',
    corner=True
)
g.figure.suptitle('Pairplot of Clinical Features by Pregnancy Risk', y=1.01,
                   fontsize=14, fontweight='bold')
g.figure.savefig('pairplot.png', dpi=150, bbox_inches='tight')
plt.show()
print("Pairplot saved as pairplot.png")