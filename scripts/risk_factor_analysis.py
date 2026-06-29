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

# Debug: print translated column names to verify
print("Translated columns:", df.columns.tolist())

# Fill NaN with 'None' for all string/object columns (because of translation differences)
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].fillna('None')

# Parse blood pressure & compute MAP
df[['systolic_bp', 'diastolic_bp']] = df['blood_pressure'].str.split('/', expand=True)
df['systolic_bp'] = pd.to_numeric(df['systolic_bp'], errors='coerce')
df['diastolic_bp'] = pd.to_numeric(df['diastolic_bp'], errors='coerce')
df['mean_arterial_pressure'] = (df['systolic_bp'] + (2 * df['diastolic_bp'])) / 3

# Derived flags
df['high_bp'] = df['systolic_bp'] >= 120
df['anemia_present'] = df['anemia'] != 'None'

# ── Print Statistics ──────────────────────────────────────────────────────────

# 1. Anemia + High BP co-occurrence
combo = df.groupby(['anemia_present', 'high_bp'])['risky_pregnancy'].apply(
    lambda x: (x == 'Yes').sum()
).reset_index()
combo.columns = ['anemia_present', 'high_bp', 'risky_count']
combo['total'] = df.groupby(['anemia_present', 'high_bp']).size().values
combo['risky_pct'] = (combo['risky_count'] / combo['total'] * 100).round(1)
print("Anemia + High BP co-occurrence with Risky Pregnancy:")
print(combo.to_string(), "\n")

# 2. VDRL & HRsAG positive rates by risk group
print("VDRL Positive Rate by Risk (%):")
print(pd.crosstab(df['risky_pregnancy'], df['vdrl'], normalize='index').round(3) * 100, "\n")

print("HRsAG Positive Rate by Risk (%):")
print(pd.crosstab(df['risky_pregnancy'], df['hrsag'], normalize='index').round(3) * 100, "\n")

# 3. Jaundice vs risk
print("Jaundice vs Risk Level:")
print(pd.crosstab(df['risky_pregnancy'], df['jaundice']), "\n")

# 4. Fetal position vs risk
print("Fetal Position vs Risk Level:")
print(pd.crosstab(df['risky_pregnancy'], df['position_of_pregnant_baby']), "\n")

# 5. Risk % by anemia severity
print("Risk % by Anemia Severity:")
print(df.groupby('anemia')['risky_pregnancy'].apply(
    lambda x: round((x == 'Yes').sum() / len(x) * 100, 1)
), "\n")

# ── Plots ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.05)
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.subplots_adjust(hspace=0.45, wspace=0.35)

GREEN, RED, ORANGE = '#2ecc71', '#e74c3c', '#f39c12'

# Plot 1: Anemia + High BP combo risk %
ax1 = axes[0, 0]
labels = ['No Anemia\nNormal BP', 'No Anemia\nHigh BP', 'Anemia\nNormal BP', 'Anemia\nHigh BP']
risky_pcts = [63.7, 100.0, 64.3, 100.0]
colors = [GREEN if p < 80 else RED for p in risky_pcts]
bars = ax1.bar(labels, risky_pcts, color=colors, edgecolor='white', linewidth=1.2)
for bar, pct in zip(bars, risky_pcts):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
             f'{pct}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
ax1.set_ylim(0, 115)
ax1.set_title('Anemia + High BP\nvs Risky Pregnancy %', fontsize=13, fontweight='bold')
ax1.set_ylabel('% Classified as Risky')
ax1.axhline(66.6, color='gray', linestyle='--', alpha=0.5, label='Baseline risk')
ax1.legend(fontsize=9)

# Plot 2: Risk % by anemia severity
ax2 = axes[0, 1]
anemia_risk = df.groupby('anemia').apply(
    lambda x: round((x['risky_pregnancy'] == 'Yes').sum() / len(x) * 100, 1)
).reset_index()
anemia_risk.columns = ['anemia', 'risky_pct']
anemia_risk['anemia'] = pd.Categorical(anemia_risk['anemia'],
                                       categories=['None', 'Minimal', 'Medium'], ordered=True)
anemia_risk = anemia_risk.sort_values('anemia')
bars2 = ax2.bar(anemia_risk['anemia'], anemia_risk['risky_pct'],
                color=[GREEN, ORANGE, RED], edgecolor='white', linewidth=1.2)
for bar, pct in zip(bars2, anemia_risk['risky_pct']):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
             f'{pct}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
ax2.set_ylim(0, 85)
ax2.set_title('Risk % by\nAnemia Severity', fontsize=13, fontweight='bold')
ax2.set_xlabel('Anemia Severity')
ax2.set_ylabel('% Classified as Risky')

# Plot 3: MAP Boxplot
ax3 = axes[0, 2]
sns.boxplot(
    data=df,
    x='risky_pregnancy',
    y='mean_arterial_pressure',
    hue='risky_pregnancy',
    palette={'No': GREEN, 'Yes': RED},
    legend=False,
    ax=ax3
)
ax3.set_title('Distribution of\nMean Arterial Pressure (MAP)', fontsize=13, fontweight='bold')
ax3.set_xlabel('Pregnancy Risk Level', fontsize=12)
ax3.set_ylabel('MAP (mmHg)', fontsize=12)

# Plot 4: Risk % by jaundice severity
ax4 = axes[1, 0]
jaundice_risk = df.groupby('jaundice').apply(
    lambda x: round((x['risky_pregnancy'] == 'Yes').sum() / len(x) * 100, 1)
).reset_index()
jaundice_risk.columns = ['jaundice', 'risky_pct']
jaundice_risk['jaundice'] = pd.Categorical(jaundice_risk['jaundice'],
                                           categories=['None', 'Minimal', 'Medium'], ordered=True)
jaundice_risk = jaundice_risk.sort_values('jaundice')
bars4 = ax4.bar(jaundice_risk['jaundice'], jaundice_risk['risky_pct'],
                color=[GREEN, ORANGE, RED], edgecolor='white', linewidth=1.2)
for bar, pct in zip(bars4, jaundice_risk['risky_pct']):
    ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
             f'{pct}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
ax4.set_ylim(0, 90)
ax4.set_title('Risk % by\nJaundice Severity', fontsize=13, fontweight='bold')
ax4.set_xlabel('Jaundice Severity')
ax4.set_ylabel('% Classified as Risky')

# Plot 5: Fetal position vs risk
ax5 = axes[1, 1]
fetal_ct = pd.crosstab(df['position_of_pregnant_baby'], df['risky_pregnancy'])
fetal_ct.plot(kind='bar', ax=ax5, color=[GREEN, RED], edgecolor='white', linewidth=1.2)
ax5.set_title('Fetal Position\nvs Risk Level', fontsize=13, fontweight='bold')
ax5.set_xlabel('Fetal Position')
ax5.set_ylabel('Number of Patients')
ax5.set_xticklabels(['Abnormal', 'Normal'], rotation=0)
ax5.legend(title='Risky Pregnancy', labels=['No', 'Yes'])
for container in ax5.containers:
    ax5.bar_label(container, fontsize=9, padding=2)

# Hide the empty 6th subplot
axes[1, 2].set_visible(False)

fig.suptitle('Risk Factor Deep-Dive Analysis — Maternal Health Dataset',
             fontsize=16, fontweight='bold', y=1.01)

plt.tight_layout()
plt.savefig('risk_factor_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved as risk_factor_analysis.png")