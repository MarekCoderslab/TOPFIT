import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
import streamlit as st


# --- Načtení dat ---
df_exploded = pd.read_csv("topfit_rozdel_cviceni.csv")

# --- Datum, týden, formátování ---
df_exploded["date"] = pd.to_datetime(df_exploded["date"])
iso = df_exploded["date"].dt.isocalendar()

df_exploded["week"] = (
    iso.year.astype(str) + "-" + iso.week.astype(str).str.zfill(2)
)
df_exploded["date_fmt"] = df_exploded["date"].dt.strftime("%d.%m.%y")
df_exploded["week_number"] = iso.week

# --- Seznam týdnů ---
all_weeks = sorted(df_exploded["week"].unique())

# --- Typy lekcí ---
summary_types = sorted(df_exploded["summary_norm"].unique())

# --- Barevná mapa ---
cmap = cm.get_cmap("Set2", len(summary_types))
color_map = {typ: cmap(i) for i, typ in enumerate(summary_types)}

def rgba_to_hex(rgba):
    return mcolors.to_hex(rgba)

colored_columns = {
    col: f"<span style='color:{rgba_to_hex(color_map[col])}'>{col}</span>"
    for col in summary_types
}

# --- Týdenní pivot ---
energy_weekly = (
    pd.pivot_table(
        df_exploded,
        index="week",
        columns="summary_norm",
        values="energy_per_category",
        aggfunc="sum"
    )
    .reindex(all_weeks, fill_value=0)
)

energy_weekly_clean = (
    energy_weekly.round(0)
    .map(lambda x: "" if pd.isna(x) else f"{int(x)} kcal")
)

pivot_colored = energy_weekly_clean.rename(columns=colored_columns)

# --- Denní pivot ---
energy_daily = (
    pd.pivot_table(
        df_exploded,
        index="date_fmt",
        columns="summary_norm",
        values="energy_per_category",
        aggfunc="sum"
    )
    .sort_index(ascending=False)
)

energy_daily_clean = (
    energy_daily.round(0)
    .map(lambda x: "" if pd.isna(x) else f"{int(x)} kcal")
)

pivot_colored_2 = energy_daily_clean.rename(columns=colored_columns)

# --- Bezpečné doplnění týdne (žádné reindex chyby) ---
week_map = (
    df_exploded[["date_fmt", "week_number"]]
    .drop_duplicates(subset="date_fmt")
    .set_index("date_fmt")["week_number"]
)

pivot_colored_2.insert(
    1,
    "Týden",
    pivot_colored_2.index.map(week_map)
)

# --- HTML tabulka pro týdenní pivot ---
html_table = pivot_colored.to_html(
    classes="centered-table",
    escape=False,
    index=True
)

# --- Graf stacked bar chart ---
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
        color=color_map[typ]
    )
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
    fontsize="small",
    title_fontsize="medium"
)

plt.tight_layout()
plt.show()



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




# --- 1) řádek: fig4 samostatně ---
col4 = st.columns(1)[0]

with col4:
    # st.subheader("Energie cvičení po týdnech podle typu lekce")
    st.pyplot(fig4)

# --- 2) Samostatný řádek: vysvětlivka PB / ZRT --- 
# st.subheader("PB = partie Prsa, Biceps, ZRT = partie Záda, Ramena, Triceps")

# --- 3) řádek: tři grafy vedle sebe ---
col1, col2, col3 = st.columns(3)

with col1:
    st.pyplot(fig1)
with col2:
    st.pyplot(fig2)
with col3:
    st.pyplot(fig3)


# --- 4) řádek: denní pivotní tabulka (pivot_colored_2) ---
col5 = st.columns(1)[0]

with col5:
    st.subheader("Energie podle typu lekce")
    html_table_2 = pivot_colored_2.to_html(
        classes="centered-table",
        escape=False,
        index=True
    )
    st.markdown(css + html_table_2, unsafe_allow_html=True)
