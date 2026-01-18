import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np

st.set_page_config(layout="wide")
st.title("Vizualizace posilování")
st.subheader("PB = Prsa/Biceps &nbsp;&nbsp;&nbsp; ZRT = Záda/Ramena/Triceps")

# ------------------------------------------------------------
# 1) Načtení dat
# ------------------------------------------------------------
df = pd.read_csv("topfit_rozdel_cviceni.csv")
df["date"] = pd.to_datetime(df["date"])

# Rok z data
df["year"] = df["date"].dt.year

# Týden z CSV (už existuje)
df["week"] = df["week"].astype(int)

# Stabilní klíč pro pivoty
df["year_week"] = df["year"].astype(str) + "-" + df["week"].astype(str).str.zfill(2)

# Typy lekcí
summary_types = sorted(df["summary_norm"].unique())


# Barvy
cmap = cm.get_cmap("Set2", len(summary_types))
color_map = {typ: cmap(i) for i, typ in enumerate(summary_types)}

def rgba_to_hex(rgba):
    return mcolors.to_hex(rgba)

colored_columns = {
    col: f"<span style='color:{rgba_to_hex(color_map[col])}'>{col}</span>"
    for col in summary_types
}

# ------------------------------------------------------------
# 2) Grafy – koláč, počty, celkový čas
# ------------------------------------------------------------
time_per_lesson = df.groupby("summary_norm")["doba_per_category"].sum()

fig1, ax1 = plt.subplots(figsize=(4, 4))
colors1 = [color_map[typ] for typ in time_per_lesson.index]
time_per_lesson.plot(kind="pie", autopct="%1.1f%%", ax=ax1, colors=colors1)
ax1.set_title("Podíl času podle typu lekce")
ax1.set_xlabel("")
ax1.set_ylabel("")

lesson_counts = df["summary_norm"].value_counts().reindex(summary_types)
fig2, ax2 = plt.subplots(figsize=(4, 4))
colors2 = [color_map[typ] for typ in lesson_counts.index]
lesson_counts.plot(kind="bar", ax=ax2, color=colors2)
ax2.set_title("Počet typů lekcí")
ax2.set_xlabel("")

time_by_type = df.groupby("summary_norm")["doba_per_category"].sum().reindex(summary_types)
fig3, ax3 = plt.subplots(figsize=(4, 4))
colors3 = [color_map[typ] for typ in time_by_type.index]
time_by_type.plot(kind="bar", ax=ax3, color=colors3)
ax3.set_title("Celkový čas podle typu")
ax3.set_xlabel("")

# ------------------------------------------------------------
# 3) Týdenní pivot – správný, stabilní
# ------------------------------------------------------------
all_weeks = sorted(df["year_week"].unique())

energy_weekly = (
    pd.pivot_table(
        df,
        index="year_week",
        columns="summary_norm",
        values="energy_per_category",
        aggfunc="sum"
    )
    .reindex(all_weeks, fill_value=0)
    .reindex(columns=summary_types, fill_value=0)
)
energy_weekly = energy_weekly.fillna(0)

# ------------------------------------------------------------
# 4) Denní pivot – date + year_week
# ------------------------------------------------------------
energy_daily = (
    pd.pivot_table(
        df,
        index="date",
        columns="summary_norm",
        values="energy_per_category",
        aggfunc="sum"
    )
    .sort_index(ascending=False)
)

# Přidání sloupce year_week
date_week_map = df[["date", "year_week"]].drop_duplicates()
energy_daily = energy_daily.merge(date_week_map, on="date", how="left")

# Přesun sloupce
cols = ["date", "year_week"] + [c for c in energy_daily.columns if c not in ["date", "year_week"]]
energy_daily = energy_daily[cols]

# Formátování
energy_daily_fmt = energy_daily.copy()
for col in summary_types:
    energy_daily_fmt[col] = energy_daily_fmt[col].map(
        lambda x: "" if pd.isna(x) else f"{int(x)} kcal"
    )

pivot_colored_2 = energy_daily_fmt.rename(columns=colored_columns)

# ------------------------------------------------------------
# 5) Stacked bar graf – týdenní energie
# ------------------------------------------------------------
fig4, ax4 = plt.subplots(figsize=(10, 6))
ax4.set_ylim(0, energy_weekly.sum(axis=1).max() * 1.1)

x = np.arange(len(all_weeks))
bottom = np.zeros(len(all_weeks))

for typ in summary_types:
    values = energy_weekly[typ].values
    ax4.bar(
        x, 
        values, 
        bottom=bottom, 
        label=typ, 
        color=color_map[typ],
        edgecolor="black",
        linewidth=0.5)
    bottom += values

ax4.set_xlabel("Týden")
ax4.set_ylabel("Energie [kcal]")
ax4.set_xticks(x)
ax4.set_xticklabels(all_weeks, rotation=90)

ax4.legend(
    title="Typ lekce",
    loc="upper center",
    bbox_to_anchor=(0.5, 1.15),
    ncol=len(summary_types),
    frameon=False,
)

plt.tight_layout()

# ------------------------------------------------------------
# 6) CSS + layout
# ------------------------------------------------------------
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
}
.centered-table th {
    background-color: #f2f2f2;
}
</style>
"""

# ------------------------------------------------------------
# 7) Streamlit layout
# ------------------------------------------------------------
st.pyplot(fig4)

col1, col2, col3 = st.columns(3)
col1.pyplot(fig1)
col2.pyplot(fig2)
col3.pyplot(fig3)

st.subheader("Denní energie podle typu lekce")
html_table_2 = pivot_colored_2.to_html(classes="centered-table", escape=False)
st.markdown(css + html_table_2, unsafe_allow_html=True)
