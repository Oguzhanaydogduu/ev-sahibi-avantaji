"""
2021-22 ve 2022-23 sezonlarını openfootball/football.json'dan çekip
football-data.org API CSV'leriyle aynı formata çevirir.

Neden? football-data.org'un ücretsiz planı bu sezonlar için 403 (restricted) döndürüyor.

Kaynak: https://github.com/openfootball/football.json (açık lisanslı, CC0)
Notlar:
- `id` sütunu sentetiktir (9.000.000'dan başlar), API id'leriyle çakışmaz.
- `utcDate` openfootball'da yerel saattir (UTC değil); analiz için önemi yok.
- Devre arası skoru bazı maçlarda kaynakta bulunmuyor (hepsi 0-0 biten maçlar), boş bırakılır.
  Notebook'taki veri kalitesi adımında bu maçların ilk yarı skoru 0-0 olarak dolduruluyor.
"""
import os

import pandas as pd
import requests

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HAM = os.path.join(PROJE, "data", "raw")

LIGLER = {
    # openfootball kodu: (API kodu, dosya öneki, referans dosya)
    "en.1": ("PL", "PL", "PL23-24.csv"),
    "es.1": ("PD", "LALIGA", "LALIGA23-24.csv"),
    "it.1": ("SA", "SERIEA", "SERIEA23-24.csv"),
    "de.1": ("BL1", "BUNDESLIGA", "BUNDESLIGA23-24.csv"),
    "fr.1": ("FL1", "LIGUE1_", "LIGUE1_23-24.csv"),
}
SEZONLAR = {"2021-22": "21-22", "2022-23": "22-23"}

# API'deki tam isim -> kısa isim eşlemesini mevcut dosyalardan öğren
api_tum = pd.concat(
    pd.read_csv(os.path.join(HAM, k, f))
    for k in ["23-24", "24-25", "25-26"]
    for f in os.listdir(os.path.join(HAM, k))
)
TAM_TO_KISA = dict(zip(api_tum["homeTeam.name"], api_tum["homeTeam.shortName"]))
TAM_TO_TLA = dict(zip(api_tum["homeTeam.name"], api_tum["homeTeam.tla"]))

# openfootball'da farklı yazılan veya 2023 sonrası ligde olmayan takımlar
EK_ISIMLER = {
    "AS Monaco": "Monaco",
    "Olympique Marseille": "Marseille",
    "Paris Saint-Germain": "PSG",
    "RC Lens": "RC Lens",
    "RC Strasbourg": "Strasbourg",
    "Stade Rennais": "Stade Rennais",
    "AC Ajaccio": "Ajaccio",
    "ESTAC Troyes": "Troyes",
    "Girondins Bordeaux": "Bordeaux",
    "Arminia Bielefeld": "Bielefeld",
    "FC Schalke 04": "Schalke",
    "Hertha BSC": "Hertha",
    "SpVgg Greuther Fürth 1903": "Greuther Fürth",
    "Norwich City FC": "Norwich",
    "Watford FC": "Watford",
    "Spezia Calcio": "Spezia",
    "UC Sampdoria": "Sampdoria",
    "US Salernitana 1919": "Salernitana",
}


def kisa_isim(tam):
    if tam in TAM_TO_KISA:
        return TAM_TO_KISA[tam]
    if tam in EK_ISIMLER:
        return EK_ISIMLER[tam]
    raise KeyError(f"Eşlenmemiş takım ismi: {tam}")


sayac = 9_000_000
for sezon, klasor_eki in SEZONLAR.items():
    klasor = os.path.join(HAM, klasor_eki)
    os.makedirs(klasor, exist_ok=True)
    for of_kod, (api_kod, onek, ref_dosya) in LIGLER.items():
        url = f"https://raw.githubusercontent.com/openfootball/football.json/master/{sezon}/{of_kod}.json"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        maclar = r.json()["matches"]

        ref = pd.read_csv(os.path.join(HAM, "23-24", ref_dosya))  # sütun düzeni ve lig bilgileri için
        sabit = ref.iloc[0]  # lig/ülke bilgileri her satırda aynı

        satirlar = []
        for m in maclar:
            sayac += 1
            ft = m["score"]["ft"]
            ht = m["score"].get("ht", [None, None])
            ev, dep = m["team1"], m["team2"]
            satirlar.append({
                "id": sayac,
                "utcDate": f"{m['date']}T{m.get('time', '00:00')}:00Z",
                "status": "FINISHED",
                "matchday": int(m["round"].split()[-1]),
                "stage": "REGULAR_SEASON",
                "homeTeam.name": ev,
                "homeTeam.shortName": kisa_isim(ev),
                "homeTeam.tla": TAM_TO_TLA.get(ev),
                "awayTeam.name": dep,
                "awayTeam.shortName": kisa_isim(dep),
                "awayTeam.tla": TAM_TO_TLA.get(dep),
                "score.winner": "HOME_TEAM" if ft[0] > ft[1] else ("AWAY_TEAM" if ft[0] < ft[1] else "DRAW"),
                "score.duration": "REGULAR",
                "score.fullTime.home": ft[0],
                "score.fullTime.away": ft[1],
                "score.halfTime.home": ht[0],
                "score.halfTime.away": ht[1],
            })

        df = pd.DataFrame(satirlar)
        for sutun in ["area.id", "area.name", "area.code", "area.flag", "competition.id",
                      "competition.name", "competition.code", "competition.type", "competition.emblem"]:
            df[sutun] = sabit[sutun]
        df["season.startDate"] = min(m["date"] for m in maclar)
        df["season.endDate"] = max(m["date"] for m in maclar)
        df["season.currentMatchday"] = df["matchday"].max()

        df = df.reindex(columns=ref.columns)  # API dosyalarıyla aynı sütun sırası
        df = df.astype({"score.halfTime.home": "Int64", "score.halfTime.away": "Int64"})
        hedef = os.path.join(klasor, f"{onek}{klasor_eki}.csv")
        df.to_csv(hedef, index=False)
        print(f"{os.path.basename(hedef):<22} {len(df)} maç kaydedildi")
