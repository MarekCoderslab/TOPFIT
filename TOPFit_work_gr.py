import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

st.set_page_config(layout="wide")
st.title("Vizualizace posilování")
st.subheader("PB = partie Prsa, Biceps, ZRT = partie Záda, Ramena, Triceps")

df = pd.read_csv("topfit_rozdel_cviceni.csv")
df["week"] = pd.to_datetime(df["date"]).dt.isocalendar().week.astype(int)

# --- 1. Koláčový graf ---
time_per_lesson = df.groupby("summary_norm")["doba_per_category"].sum()
fig1, ax1 = plt.subplots(figsize=(4, 4))
time_per_lesson.plot(kind="pie", autopct="%1.1f%%", ax=ax1)
ax1.set_title("Podíl času podle typu lekce")
ax1.set_ylabel("")

# --- 2. Počet typů lekcí ---
fig2, ax2 = plt.subplots(figsize=(4, 4))
df["summary_norm"].value_counts().plot(kind="bar", ax=ax2)
ax2.set_title("Počet typů lekcí")
ax2.set_xlabel("Typ")
ax2.set_ylabel("Počet")

# --- 3. Celkový čas podle typu ---
fig3, ax3 = plt.subplots(figsize=(4, 4))
df.groupby("summary_norm")["doba_per_category"].sum().plot(kind="bar", ax=ax3)
ax3.set_title("Celkový čas podle typu")
ax3.set_xlabel("Typ")
ax3.set_ylabel("Minuty")

# --- 4. Čas po týdnech s barvami ---
all_weeks = list(range(df["week"].min(), df["week"].max() + 1))
weekly_minutes = df.groupby("week")["doba_per_category"].sum().reindex(all_weeks, fill_value=0)
weekly_counts = df.groupby("week").size().reindex(all_weeks, fill_value=0)
norm = plt.Normalize(weekly_counts.min(), weekly_counts.max())
colors = cm.coolwarm(norm(weekly_counts.values))

fig4, ax4 = plt.subplots(figsize=(4, 4))
x = np.arange(len(all_weeks))
bars = ax4.bar(x, weekly_minutes.values, color=colors)
ax4.set_title("Čas cvičení po týdnech")
ax4.set_xlabel("Týden")
ax4.set_ylabel("Minuty")
ax4.set_xticks(x)
ax4.set_xticklabels(all_weeks, rotation=90)

# --- Layout: 4 sloupce vedle sebe ---
cols = st.columns(4)
figs = [fig1, fig2, fig3, fig4]

for i in range(4):
    with cols[i]:
        st.markdown("<div style='display: flex; align-items: center; justify-content: center; height: 100%;'>", unsafe_allow_html=True)
        st.pyplot(figs[i])
        st.markdown("</div>", unsafe_allow_html=True)


# Převod datumu na měsíc
df_exploded["month"] = pd.to_datetime(df_exploded["date"]).dt.to_period("M")

# Pivotní tabulka: součet energie podle měsíce a summary_norm
energy_pivot = pd.pivot_table(
    df_exploded,
    index="date",
    columns="summary_norm",
    values="energy_per_category",
    aggfunc="sum",
    # fill_value=0
)

# Nahrazení NaN prázdným řetězcem

energy_pivot_clean = energy_pivot.replace({pd.NA: "", None: "", float("nan"): ""})
# energy_pivot_rounded = energy_pivot.round(0).astype("Int64")

energy_pivot_rounded = energy_pivot.round(0)

# Převedeme na string, zaokrouhlíme, a nahradíme NaN prázdným řetězcem
energy_pivot_clean = energy_pivot_rounded.map(
    lambda x: "" if pd.isna(x) else str(int(x))
)

st.subheader("Pivotní tabulka: čas cvičení podle týdne a typu")
st.dataframe(energy_pivot_clean)
