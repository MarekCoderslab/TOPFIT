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

import matplotlib.colors as mcolors

summary_types = sorted(df["summary_norm"].unique())
cmap = cm.get_cmap("Set2", len(summary_types))  # nebo "tab10", "Paired", "Accent"

color_map = {typ: cmap(i) for i, typ in enumerate(summary_types)}

# --- 1. Koláčový graf ---
time_per_lesson = df.groupby("summary_norm")["doba_per_category"].sum()
# fig1, ax1 = plt.subplots(figsize=(4, 4))
# time_per_lesson.plot(kind="pie", autopct="%1.1f%%", ax=ax1)
# ax1.set_title("Podíl času podle typu lekce")
# ax1.set_ylabel("")

fig1, ax1 = plt.subplots(figsize=(4, 4))
colors1 = [color_map[typ] for typ in time_per_lesson.index]
time_per_lesson.plot(kind="pie", autopct="%1.1f%%", ax=ax1, colors=colors1)
ax1.set_title("Podíl času podle typu lekce")
ax1.set_ylabel("")


# --- 2. Počet typů lekcí ---
# fig2, ax2 = plt.subplots(figsize=(4, 4))
# df["summary_norm"].value_counts().plot(kind="bar", ax=ax2)
# ax2.set_title("Počet typů lekcí")
# ax2.set_xlabel("Typ")
# ax2.set_ylabel("Počet")

fig2, ax2 = plt.subplots(figsize=(4, 4))
lesson_counts = df["summary_norm"].value_counts().reindex(summary_types)
colors2 = [color_map[typ] for typ in lesson_counts.index]
lesson_counts.plot(kind="bar", ax=ax2, color=colors2)
ax2.set_title("Počet typů lekcí")
ax2.set_xlabel("Typ")
ax2.set_ylabel("Počet")


# --- 3. Celkový čas podle typu ---
# fig3, ax3 = plt.subplots(figsize=(4, 4))
# df.groupby("summary_norm")["doba_per_category"].sum().plot(kind="bar", ax=ax3)
# ax3.set_title("Celkový čas podle typu")
# ax3.set_xlabel("Typ")
# ax3.set_ylabel("Minuty")

fig3, ax3 = plt.subplots(figsize=(4, 4))
time_by_type = df.groupby("summary_norm")["doba_per_category"].sum().reindex(summary_types)
colors3 = [color_map[typ] for typ in time_by_type.index]
time_by_type.plot(kind="bar", ax=ax3, color=colors3)
ax3.set_title("Celkový čas podle typu")
ax3.set_xlabel("Typ")
ax3.set_ylabel("Minuty")


# --- 4. Čas po týdnech s barvami ---
# all_weeks = list(range(df["week"].min(), df["week"].max() + 1))
# weekly_minutes = df.groupby("week")["doba_per_category"].sum().reindex(all_weeks, fill_value=0)
# weekly_counts = df.groupby("week").size().reindex(all_weeks, fill_value=0)
# norm = plt.Normalize(weekly_counts.min(), weekly_counts.max())
# colors = cm.coolwarm(norm(weekly_counts.values))

# fig4, ax4 = plt.subplots(figsize=(4, 4))
# x = np.arange(len(all_weeks))
# bars = ax4.bar(x, weekly_minutes.values, color=colors)
# ax4.set_title("Čas cvičení po týdnech")
# ax4.set_xlabel("Týden")
# ax4.set_ylabel("Minuty")
# ax4.set_xticks(x)
# ax4.set_xticklabels(all_weeks, rotation=90)

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# --- Přehled týdnů ---
all_weeks = list(range(df["week"].min(), df["week"].max() + 1))

# --- Agregace: týden × typ lekce ---
weekly_summary = df.groupby(["week", "summary_norm"])["doba_per_category"].sum().unstack(fill_value=0)
weekly_summary = weekly_summary.reindex(all_weeks, fill_value=0)

# --- Barevná mapa pro typy lekcí ---
summary_types = sorted(df["summary_norm"].unique())  # stabilní pořadí
cmap = cm.get_cmap("Set2", len(summary_types))       # pastelová paleta
color_map = {typ: cmap(i) for i, typ in enumerate(summary_types)}

# --- Vykreslení stacked bar chart ---
fig4, ax4 = plt.subplots(figsize=(6, 4))
x = np.arange(len(all_weeks))
bottom = np.zeros(len(all_weeks))

for typ in summary_types:
    ax4.bar(
        x,
        weekly_summary[typ].values,
        bottom=bottom,
        label=typ,
        color=color_map[typ]
    )
    bottom += weekly_summary[typ].values

# --- Osy a legenda ---
# ax4.set_title("Čas cvičení po týdnech podle typu lekce")
ax4.set_xlabel("Týden")
ax4.set_ylabel("Minuty")
ax4.set_xticks(x)
ax4.set_xticklabels(all_weeks, rotation=90)
ax4.legend(
    title="Typ lekce",
    loc="upper center",
    bbox_to_anchor=(0.5, 1.15),
    ncol=len(summary_types),
    frameon=False,
    fontsize="small",
    title_fontsize="medium"
)



# --- Načtení dat ---
df_exploded = pd.read_csv("topfit_rozdel_cviceni.csv")
df_exploded["date"] = pd.to_datetime(df_exploded["date"])
df_exploded["week"] = df_exploded["date"].dt.isocalendar().week.astype(int)

# --- Barevná mapa pro typy lekcí ---
summary_types = sorted(df_exploded["summary_norm"].unique())
cmap = cm.get_cmap("Set2", len(summary_types))
color_map = {typ: cmap(i) for i, typ in enumerate(summary_types)}

def rgba_to_hex(rgba):
    return mcolors.to_hex(rgba)

colored_columns = {
    col: f"<span style='color:{rgba_to_hex(color_map[col])}'>{col}</span>"
    for col in summary_types
}

# --- Pivotní tabulka: součet energie podle data a typu lekce ---
energy_pivot = pd.pivot_table(
    df_exploded,
    index=["date", "week"],
    columns="summary_norm",
    values="energy_per_category",
    aggfunc="sum"
)

# --- Zaokrouhlení a čištění ---
energy_pivot_rounded = energy_pivot.round(0)
energy_pivot_clean = energy_pivot_rounded.map(
    lambda x: "" if pd.isna(x) else f"{int(x)} kcal"
)
energy_pivot_sorted = energy_pivot_clean.sort_index(ascending=False)

# --- Přejmenování sloupců podle barevné mapy ---
pivot_colored = energy_pivot_sorted.rename(columns=colored_columns)

# --- CSS pro centrovanou tabulku ---
css = """
<style>
.centered-table {
    width: 100%;
    border-collapse: collapse;
    text-align: center;
}
.centered-table th, .centered-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
}
.centered-table th {
    background-color: #f2f2f2;
}
</style>
"""



# --- Layout: 4 sloupce vedle sebe ---
cols = st.columns(4)
figs = [fig1, fig2, fig3, fig4]

col1, col2, col3 = st.columns(3)

with col1:
    st.pyplot(fig1)
with col2:
    st.pyplot(fig2)
with col3:
    st.pyplot(fig3)

col4, col5 = st.columns([1, 1])  # můžeš upravit poměr např. [1.2, 1] podle šířky tabulky

with col4:
    st.subheader("Pivotní tabulka: čas cvičení podle dne a druhu cvičení")
    html_table = pivot_colored.to_html(classes="centered-table", escape=False, index=True)
    st.markdown(css + html_table, unsafe_allow_html=True)    

with col5:
    st.subheader("Čas cvičení po týdnech podle typu lekce")
    st.pyplot(fig4)