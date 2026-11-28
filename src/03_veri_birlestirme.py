"""
data/raw altındaki 25 lig-sezon CSV'sini tek bir analiz dosyasında birleştirir.

Çıktılar (data/ klasörü):
- tum_ligler_birlesik.csv  -> Kaggle / Python için
- tum_ligler_birlesik.xlsx -> Excel için (game.score metin olarak, tarihe dönüşmez)

Sütunlar: league, season + 13 maç sütunu
"""
import glob
import os

import pandas as pd

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI = os.path.join(PROJE, "data")

LIG_ISIMLERI = {"PL": "Premier League", "PD": "La Liga", "SA": "Serie A",
                "BL1": "Bundesliga", "FL1": "Ligue 1"}

# openfootball (2021-23) tam isimlerini API (2023-26) tam isimleriyle aynı yap
ISIM_DUZELT = {
    "AS Monaco": "AS Monaco FC",
    "Olympique Marseille": "Olympique de Marseille",
    "Paris Saint-Germain": "Paris Saint-Germain FC",
    "RC Lens": "Racing Club de Lens",
    "RC Strasbourg": "RC Strasbourg Alsace",
    "Stade Rennais": "Stade Rennais FC 1901",
}
# 2023 sonrası ligde olmayan takımlar için kısaltma (API'de karşılığı yok)
EK_TLA = {
    "AC Ajaccio": "ACA", "ESTAC Troyes": "TRO", "Girondins Bordeaux": "BOR",
    "Arminia Bielefeld": "DSC", "FC Schalke 04": "S04", "Hertha BSC": "BSC",
    "SpVgg Greuther Fürth 1903": "SGF", "Norwich City FC": "NOR", "Watford FC": "WAT",
    "Spezia Calcio": "SPE", "UC Sampdoria": "SAM", "US Salernitana 1919": "SAL",
}

ham = pd.concat(
    (pd.read_csv(f) for f in sorted(glob.glob(os.path.join(VERI, "raw", "*", "*.csv")))),
    ignore_index=True,
)
print(f"Ham satır: {len(ham):,}")

ham = ham.drop_duplicates(subset="id")
hukmen = (ham["status"] != "FINISHED").sum()
ham = ham[ham["status"] == "FINISHED"]
print(f"Hükmen/oynanmamış maç çıkarıldı: {hukmen}")

for taraf in ["homeTeam", "awayTeam"]:
    ham[f"{taraf}.name"] = ham[f"{taraf}.name"].replace(ISIM_DUZELT)
tla = dict(zip(ham["homeTeam.name"], ham["homeTeam.tla"]))
tla = {isim: kod for isim, kod in tla.items() if pd.notna(kod)} | EK_TLA

yil = pd.to_datetime(ham["season.startDate"]).dt.year
df = pd.DataFrame({
    "league": ham["competition.code"].map(LIG_ISIMLERI),
    "season": yil.astype(str) + "-" + (yil + 1).astype(str).str[-2:],
    "utcDate": ham["utcDate"],
    "matchday": ham["matchday"].astype(int),
    "area.code": ham["area.code"],
    "homeTeam.name": ham["homeTeam.name"],
    "homeTeam.tla": ham["homeTeam.name"].map(tla),
    "awayTeam.name": ham["awayTeam.name"],
    "awayTeam.tla": ham["awayTeam.name"].map(tla),
    "score.winner": ham["score.winner"],
    "score.home": ham["score.fullTime.home"].astype(int),
    "score.away": ham["score.fullTime.away"].astype(int),
    "score.halfTime.home": ham["score.halfTime.home"].astype("Int64"),
    "score.halfTime.away": ham["score.halfTime.away"].astype("Int64"),
})
df["game.score"] = df["score.home"].astype(str) + "-" + df["score.away"].astype(str)
df = df.sort_values(["league", "season", "utcDate"]).reset_index(drop=True)

assert df[["homeTeam.tla", "awayTeam.tla"]].notna().all().all(), "Kısaltması olmayan takım var"

df.to_csv(os.path.join(VERI, "tum_ligler_birlesik.csv"), index=False, encoding="utf-8-sig")
df.to_excel(os.path.join(VERI, "tum_ligler_birlesik.xlsx"), index=False, sheet_name="TUM_LIGLER")
print(f"Kaydedildi: {len(df):,} maç, {df.shape[1]} sütun")
print(pd.crosstab(df["league"], df["season"], margins=True))
