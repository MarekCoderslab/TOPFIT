


# %% Bar Kcal dle svalu
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
st.pyplot(plt)

df = pd.read_csv("topfit_rozdel_cviceni.csv")

# Měsíc jako perioda
df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")

# Součet energie za kombinaci měsíc × summary
energy_sum = df.groupby(["month", "summary_norm"])["energy_per_category"].sum().unstack(fill_value=0)

# Graf – stacked bar chart
energy_sum.plot(kind="bar", stacked=True, figsize=(12,6))
plt.title("Součet energie za měsíc podle summary (kcal)")
plt.xlabel("Měsíc")
plt.ylabel("Energie (kcal)")
plt.xticks(rotation=45)
plt.legend(title="Summary")
plt.show()



# %% koláč
import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv("topfit_rozdel_cviceni.csv")

# součet času (doba) podle typu lekce
time_per_lesson = df.groupby("summary_norm")["doba_per_category"].sum()

# koláčový graf
time_per_lesson.plot(
    kind="pie",
    autopct="%1.1f%%",
    figsize=(6,6)
)
plt.title("Podíl času podle typu lekce (minuty)")
plt.ylabel("")  # odstraní popisek y-osi
plt.show()



# %% Počet dle svalu
import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv("topfit_rozdel_cviceni.csv")

df["summary_norm"].value_counts().plot(kind="bar", figsize=(8,5))
plt.title("Počet jednotlivých typů lekcí")
plt.xlabel("Typ lekce")
plt.ylabel("Počet")
plt.show()


# %% čas dle svalu
import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv("topfit_rozdel_cviceni.csv")

df.groupby("summary_norm")["doba_per_category"].sum().plot(kind="bar", figsize=(8,5))
plt.title("Celkový čas podle typu lekce")
plt.ylabel("Celkový čas [min]")
plt.xlabel("Typ lekce")
plt.show()


# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
df = pd.read_csv("topfit_rozdel_cviceni.csv")

# jistota: ISO týden jako int
df["week"] = pd.to_datetime(df["date"]).dt.isocalendar().week.astype(int)

# kompletní rozsah týdnů (v rámci dat v df)
all_weeks = pd.RangeIndex(df["week"].min(), df["week"].max() + 1)

# součet energie po týdnech (0 pro chybějící týdny)
weekly_energy = (
    df.groupby("week", observed=True)["energy"]
      .sum(min_count=1)              # když v týdnu není žádná energie, zůstane NaN
      .reindex(all_weeks, fill_value=0)
      .fillna(0)
)

# počet lekcí po týdnech (pro popisky)
weekly_counts = (
    df.groupby("week", observed=True)
      .size()
      .reindex(all_weeks, fill_value=0)
)

# graf
ax = weekly_energy.plot(kind="line", marker="o", figsize=(12, 5))
ax.set_ylim(0, 1000)
plt.title("Celková energie po týdnech (kcal)")
plt.xlabel("Číslo týdne v roce")
plt.ylabel("Energie (kcal)")
plt.xticks(list(all_weeks))
plt.grid(True)

# popisky: počet lekcí nad body
offset = max(1, weekly_energy.max() * 0.03)  # drobný odsaz
for week, value in weekly_energy.items():
    ax.text(week, value + offset, str(int(weekly_counts.loc[week])), ha="center", va="bottom")

plt.show()



# %% Týdny
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd

# --- jistota: vytvoř sloupec week jako int ---
df["week"] = pd.to_datetime(df["date"]).dt.isocalendar().week.astype(int)

# kompletní rozsah týdnů (int list)
start_week = int(df["week"].min())
end_week = int(df["week"].max())
all_weeks = list(range(start_week, end_week + 1))

# součet minut (doba) po týdnech, přeuspořádaný podle all_weeks
weekly_minutes = (
    df.groupby("week", observed=True)["doba_per_category"]
      .sum()
      .reindex(all_weeks, fill_value=0)
      .astype(float)
)

# počet lekcí po týdnech (pro barvy / popisky)
weekly_counts = (
    df.groupby("week", observed=True)
      .size()
      .reindex(all_weeks, fill_value=0)
      .astype(int)
)

# --- barevná škála podle počtu lekcí ---
vmin = weekly_counts.min()
vmax = weekly_counts.max()
# zabrání dělení nulou, když jsou všechny hodnoty stejné
if vmin == vmax:
    norm = plt.Normalize(vmin - 1, vmax + 1)
else:
    norm = plt.Normalize(vmin, vmax)
cmap = cm.get_cmap("coolwarm")   # nebo "viridis", "plasma" atd.
colors = cmap(norm(weekly_counts.values))

# --- vykreslení ---
fig, ax = plt.subplots(figsize=(12, 5))
x = np.arange(len(all_weeks))  # pozice na ose x

bars = ax.bar(x, weekly_minutes.values, color=colors)
ax.set_ylim(0, max(130, weekly_minutes.max() * 1.15))  # minimální max 130, nebo dynamické
ax.set_title("Celkový čas cvičení po týdnech")
ax.set_xlabel("Číslo týdne v roce")
ax.set_ylabel("Minuty")
ax.set_xticks(x)
ax.set_xticklabels(all_weeks, rotation=0)
ax.grid(axis="y")

# přidání počtu lekcí nad sloupce
offset = max(1, weekly_minutes.max() * 0.03)
for i, (val, cnt) in enumerate(zip(weekly_minutes.values, weekly_counts.values)):
    ax.text(i, val + offset, str(int(cnt)), ha='center', va='bottom')

plt.show()



# %% [markdown]
# Sekvenční (pro hodnoty od nízké po vysokou)
# 
#     viridis – tmavě modrá → žlutá, velmi dobře čitelná
# 
#     plasma – fialová → žlutá, kontrastní a živá
# 
#     inferno – černá → žlutá, hodně kontrastu
# 
#     magma – tmavá → světle fialová, jemnější než inferno
# 
#     cividis – modro-žlutá, vhodné pro barevně slabozraké
# 
# 2️⃣ Divergentní (pro hodnoty kolem střední hodnoty)
# 
#     coolwarm – modrá ↔ červená
# 
#     bwr – modrá ↔ bílá ↔ červená
# 
#     seismic – tmavě modrá ↔ bílá ↔ červená
# 
# 3️⃣ Kategorické / diskrétní
# 
#     tab10, tab20, Set1, Set2, Accent – pro oddělení skupin/barvy jednotlivých kategorií


