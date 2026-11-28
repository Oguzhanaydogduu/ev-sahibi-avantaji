"""
2023-24, 2024-25 ve 2025-26 sezonlarını football-data.org API v4'ten çeker.
Her lig-sezon için ayrı bir CSV dosyası yazar: data/raw/<sezon>/<LIG><sezon>.csv

Kullanım:
    1) https://www.football-data.org/client/register adresinden ücretsiz API anahtarı alın.
    2) Anahtarı ortam değişkeni olarak tanımlayın:
         Windows (PowerShell):  $env:FOOTBALL_DATA_API_KEY = "anahtariniz"
         macOS / Linux:         export FOOTBALL_DATA_API_KEY="anahtariniz"
    3) python src/01_api_veri_cekme.py

Notlar:
- Ücretsiz plan 2021-22 ve 2022-23 sezonları için 403 (restricted) döndürüyor.
  Bu sezonlar 02_eski_sezonlar_openfootball.py ile çekiliyor.
- Ücretsiz plan dakikada 10 istek sınırı koyuyor, istekler arasında 7 saniye bekleniyor.
"""
import os
import time

import pandas as pd
import requests

PROJE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HAM = os.path.join(PROJE, "data", "raw")

API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY")
if not API_KEY:
    raise SystemExit("FOOTBALL_DATA_API_KEY ortam değişkeni tanımlı değil.")
headers = {"X-Auth-Token": API_KEY}

# API lig kodu -> dosya öneki
LIGLER = {"PL": "PL", "PD": "LALIGA", "SA": "SERIEA", "BL1": "BUNDESLIGA", "FL1": "LIGUE1_"}
# API'deki sezon parametresi (başlangıç yılı) -> klasör/dosya eki
SEZONLAR = {2023: "23-24", 2024: "24-25", 2025: "25-26"}

for yil, sezon in SEZONLAR.items():
    os.makedirs(os.path.join(HAM, sezon), exist_ok=True)
    for kod, onek in LIGLER.items():
        url = f"https://api.football-data.org/v4/competitions/{kod}/matches?season={yil}"
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()

        # Hata kontrolü: 403 (plan kısıtı) veya 429 (çağrı limiti) gelirse boş dosya yazma, dur
        if response.status_code != 200:
            raise SystemExit(f"{kod} {sezon} - API hatası {response.status_code}: {data.get('message')}")

        # JSON içindeki maçlar listesini alıyoruz
        matches = data.get("matches", [])
        if not matches:
            raise SystemExit(f"{kod} {sezon} - API boş maç listesi döndürdü, dosya yazılmadı.")

        # Veriyi yapılandırılmış bir tabloya dönüştürüp CSV olarak kaydediyoruz
        df = pd.json_normalize(matches)
        hedef = os.path.join(HAM, sezon, f"{onek}{sezon}.csv")
        df.to_csv(hedef, index=False)
        print(f"{os.path.basename(hedef):<22} {len(df)} maç kaydedildi")

        time.sleep(7)
