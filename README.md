# Evinde Kazanmak: Avrupa'nın 5 Büyük Liginde Ev Sahibi Avantajı

Google Data Analytics sertifika programının son vaka çalışması için kendi konumu seçtim: futbolda ev sahibi avantajı gerçekten var mı, varsa ne kadar büyük?

Premier League, La Liga, Serie A, Bundesliga ve Ligue 1'de 2021-22 ile 2025-26 arasındaki beş sezonda oynanan 8.905 maçı inceledim. Veriyi hazır bir veri setinden almadım. İki farklı kaynaktan kendim çektim, ortak bir formata getirdim, birleştirdim ve kalite kontrolünden geçirdikten sonra Python ile analiz ettim.

## Kısaca ne buldum?

Ev sahibi takımlar maçların %43,5'ini kazanıyor, deplasman takımları ise %31,1'ini. Ev sahibi olmak maç başına ortalama 0,37 puan, bir sezonda takım başına yaklaşık 7 puan değerinde.

Bunun şans eseri olmadığını binom testiyle sınadım. Beraberlikleri çıkardığımda kazananı belli olan maçların %58'ini ev sahibi kazanıyor ve beş ligin hepsinde p-değeri 0,001'in altında.

Asıl ilginç olan, avantajın her yerde aynı olmaması:

- Ligler arasında ciddi fark var. La Liga'da ev sahibi olmak maç başına +0,53 puan getirirken Serie A'da bu değer +0,24'te kalıyor.
- Avantaj sezondan sezona dalgalanıyor. Örneğin Bundesliga'da 2022-23'te +0,58 olan değer 2024-25'te +0,08'e düşmüş.
- Bazı takımlar evinde bambaşka bir takıma dönüşüyor. Atlético Madrid evinde deplasmana göre maç başına 0,83 puan fazla topluyor. Toulouse ise deplasmanda daha başarılı.
- Ev sahibi öne geçtiğinde skoru daha iyi koruyor. İlk yarıyı önde kapatan ev sahibi maçların %77,5'ini kazanırken aynı durumdaki deplasman takımı %67,3'ünü kazanıyor.

## Veriyi nasıl topladım?

2023-24, 2024-25 ve 2025-26 sezonlarını football-data.org API'sinden çektim. Her lig ve sezon için gelen maç listesini pandas ile tabloya çevirip ayrı bir CSV olarak kaydettim. API bir hata döndürdüğünde script boş dosya yazmak yerine duruyor. Böylece istek limiti ya da plan kısıtı yüzünden fark edilmeden eksik veri oluşmuyor.

2021-22 ve 2022-23 sezonlarında API'nin ücretsiz planı erişim vermedi (HTTP 403). Bu iki sezonu açık lisanslı openfootball/football.json deposundan aldım. Bu kaynağın formatı farklı olduğu için her maçı API dosyalarıyla aynı sütun yapısına çeviren ayrı bir script yazdım. En çok uğraştıran kısım takım isimleri oldu. API dosyalarındaki isim eşleşmelerini otomatik çıkardım, openfootball'da farklı yazılan ya da sonraki sezonlarda ligde olmayan 18 takımı elle eşledim.

Sonuçta her lig ve sezon için bir tane olmak üzere 25 CSV dosyası elde ettim.

## Birleştirme ve temizlik

25 dosyayı birleştirdiğimde 8.908 satır vardı. Bunlardan hükmen sonuçlanan 3 maçı çıkardım: Union Berlin-Bochum (Bundesliga 2024-25), Montpellier-Saint-Étienne (Ligue 1 2024-25) ve Nantes-Toulouse (Ligue 1 2025-26). Bu maçların skoru sahada belirlenmediği için ev sahibi avantajını ölçmek için uygun değiller.

İki kaynakta farklı yazılan altı Fransız takımının ismini eşitledim, böylece aynı takım iki ayrı takım gibi sayılmadı. Analiz için gereken 15 sütunu tuttum, geri kalanını çıkardım.

Analize başlamadan önce beş kalite kontrolü yaptım: tekrar eden maç, eksik skor, eksik ilk yarı skoru, kazanan bilgisiyle skor arasındaki çelişki ve ilk yarı golünün maç sonundan fazla olması. Tek sorun 237 maçta ilk yarı skorunun boş olmasıydı. Hepsi openfootball'dan gelen maçlardı ve hepsi 0-0 bitmişti. Kaynak, golsüz maçlarda ilk yarı skorunu boş bırakmış. Maç 0-0 bittiyse ilk yarı da 0-0 olmak zorunda olduğu için bu skorları 0-0 olarak doldurdum. Veriyi ayrıca gerçek puan tablolarıyla karşılaştırarak doğruladım (örneğin Manchester City 2021-22'de 93, Napoli 2022-23'te 90 puan).

Lig ve sezon bazında maç sayıları:

| Lig | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26 | Toplam |
|---|---|---|---|---|---|---|
| Premier League | 380 | 380 | 380 | 380 | 380 | 1.900 |
| La Liga | 380 | 380 | 380 | 380 | 380 | 1.900 |
| Serie A | 380 | 380 | 380 | 380 | 380 | 1.900 |
| Bundesliga | 306 | 306 | 306 | 305 | 306 | 1.529 |
| Ligue 1 | 380 | 380 | 306 | 305 | 305 | 1.676 |

Ligue 1'de 2023'te takım sayısı 20'den 18'e indiği için maç sayısı da düşüyor. Bir maçlık eksikler çıkardığım hükmen maçlardan geliyor.

## Analiz

Ev sahibi avantajını ölçmek için basit bir endeks kullandım: ev sahibinin maç başına aldığı puandan deplasman takımının maç başına aldığı puanı çıkardım.

Analizi beş soru üzerine kurdum:

1. Ev sahibi avantajı gerçekten var mı? Bunun için sonuç dağılımına baktım ve her lig için binom testi yaptım.
2. Avantaj her ligde aynı mı? Lig bazında puan, galibiyet oranı ve gol farkını karşılaştırdım.
3. Avantaj zaman içinde sabit mi? Lig ve sezon kırılımında bir ısı haritası çizdim.
4. Hangi takımlar evinde bambaşka? En az 38 iç saha maçı olan takımların iç ve dış saha performansını karşılaştırdım.
5. Avantaj sahaya nasıl yansıyor? Yarılara göre gol ortalamalarına ve ilk yarıyı önde kapatanların kazanma oranına baktım.

Lig bazında sonuçlar:

| Lig | Maç | Ev galibiyeti | Beraberlik | Deplasman galibiyeti | Avantaj endeksi | Gol farkı |
|---|---|---|---|---|---|---|
| La Liga | 1.900 | %45,7 | %26,2 | %28,1 | +0,53 | +0,36 |
| Bundesliga | 1.529 | %44,1 | %24,9 | %31,0 | +0,39 | +0,36 |
| Premier League | 1.900 | %44,2 | %23,9 | %31,9 | +0,37 | +0,27 |
| Ligue 1 | 1.676 | %43,5 | %24,5 | %32,0 | +0,35 | +0,26 |
| Serie A | 1.900 | %40,4 | %27,2 | %32,4 | +0,24 | +0,18 |

Grafiklerin ve kodun tamamı notebook'ta.

## Önerilerim

Senaryoda bu analizi maç tahminleri yayınlayan bir spor veri platformu için yapıyorum. Platformun modeli her maçta ev sahibine sabit bir avantaj tanıyor. Bulgulara göre önerilerim şunlar:

- Tek bir değer yerine her lig için ayrı bir ev sahibi katsayısı kullanılmalı. Tek değer La Liga'da avantajı olduğundan düşük, Serie A'da olduğundan yüksek gösterir.
- Katsayı her sezon güncellenmeli, ama tek sezona göre değil, son 3-5 sezonun ortalamasına göre. Tek sezonluk değerler çok oynak.
- İç ve dış saha performansı arasındaki fark ligin çok üstünde olan takımlar için ayrıca bir düzeltme eklenebilir.
- İçerik tarafında "evinde yenilmez" ya da "deplasman uzmanı" takımlar gibi hikâyeler bu veriyle desteklenebilir.

Bu analiz avantajın varlığını ve büyüklüğünü gösteriyor, nedenini göstermiyor. Seyirci sayısı, seyahat mesafesi, takım gücü ya da xG gibi değişkenler veride yok. Bir sonraki adımda bunları ve seyircisiz oynanan COVID sezonlarını eklemek isterim. Seyircisiz sezonlar, taraftarın etkisini ölçmek için doğal bir deney sunuyor.

## Depodaki dosyalar

- `data/raw/`: kaynaklardan çektiğim 25 ham CSV dosyası, sezon klasörlerine ayrılmış
- `data/tum_ligler_birlesik.csv`: temizlenmiş ve birleştirilmiş analiz verisi
- `data/lig_ozet_ev_sahibi_avantaji.csv`: analizin lig bazlı özet çıktısı
- `src/01_api_veri_cekme.py`: 2023-26 sezonlarını API'den çeken script
- `src/02_eski_sezonlar_openfootball.py`: 2021-23 sezonlarını openfootball'dan çekip aynı formata çeviren script
- `src/03_veri_birlestirme.py`: 25 dosyayı tek analiz dosyasında birleştiren script
- `notebooks/ev_sahibi_avantaji.ipynb`: analizin tamamı

Birleştirilmiş veride her satır bir maç. Sütunlar şöyle: lig, sezon, tarih, hafta, ülke kodu, ev sahibi ve deplasman takımının adı ve kısaltması, kazanan, maç sonu skoru, ilk yarı skoru ve metin olarak skor.

## Çalıştırmak isterseniz

Veri depoda hazır olduğu için analizi doğrudan çalıştırabilirsiniz:

```bash
pip install -r requirements.txt
jupyter notebook notebooks/ev_sahibi_avantaji.ipynb
```

Veriyi sıfırdan üretmek isterseniz football-data.org'dan ücretsiz bir API anahtarı alıp `FOOTBALL_DATA_API_KEY` ortam değişkenine yazmanız, sonra `src/` klasöründeki üç scripti sırayla çalıştırmanız yeterli. openfootball scripti takım isimlerini 2023-24 dosyalarından öğrendiği için önce API scriptini çalıştırmak gerekiyor.

## Kullandığım araçlar

Python (pandas, NumPy, Matplotlib, SciPy, requests), Jupyter Notebook, VS Code ve Kaggle.

Veri yalnızca takım ve skor bilgisi içeriyor. 2021-23 verisi CC0 lisanslı openfootball deposundan, 2023-26 verisi football-data.org'dan alındı ve servisin kullanım koşullarına tabi.

Oğuzhan Aydoğdu, [GitHub](https://github.com/Oguzhanaydogduu)
