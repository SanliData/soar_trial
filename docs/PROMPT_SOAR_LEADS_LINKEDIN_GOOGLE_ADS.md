***REMOVED*** Prompt: SOAR Lead'leri LinkedIn Ads + Google Ads Entegrasyonu

Aşağıdaki metni Cursor'a vererek SOAR'dan çıkan lead'leri LinkedIn Ads'e birebir map'leme ve Google Ads + LinkedIn Ads birlikte kullanım yeteneğini uygulamaya eklemesini isteyebilirsin.

---

***REMOVED******REMOVED*** Cursor'a verilecek prompt (kopyala-yapıştır)

```
SOAR B2B uygulamasına aşağıdaki iki yetenek eklensin. Mevcut API, export ve plan/result yapısına uyumlu olsun.

---

***REMOVED******REMOVED*** 1) SOAR lead'lerini LinkedIn Ads kampanyasına birebir map'leme

**Amaç:** SOAR Results Hub / export'tan çıkan lead listesini (firma + karar verici / persona) LinkedIn Ads Campaign Manager'da hedef kitle (audience) olarak kullanmak. Yani SOAR'dan export edilen CSV/veri ile LinkedIn'de "Matched Audiences" veya "Uploaded List" ile birebir eşleşme.

**İstenenler:**
- Backend: SOAR export formatında (veya ek bir format) LinkedIn Ads için uygun upload formatı üret.
  - LinkedIn'in beklediği alanlar: email, first name, last name, company name, job title vb. (LinkedIn Matched Audiences / Lead Gen Form alanlarına göre).
  - Mevcut export (CSV/PDF) alanları: company name, address, city, zip, persona role, contact availability. Bunları LinkedIn'e uygun kolonlara map'leyen bir "Export for LinkedIn Ads" seçeneği ekle.
- Frontend: Results Hub'da veya Export dropdown'da "Export for LinkedIn Ads" (veya "LinkedIn Ads'e aktar") seçeneği.
  - Kullanıcı tıkladığında: SOAR'daki company name, persona role, varsa contact (email/name) bilgisi LinkedIn upload formatına dönüştürülüp indirilsin (CSV). İsteğe bağlı: kısa bir "Nasıl kullanılır" metni (LinkedIn Campaign Manager > Audiences > Upload list adımları).
- Dokümantasyon: "SOAR lead'lerini LinkedIn Ads'e birebir map'leme" adımlarını anlatan kısa bir kullanım rehberi (markdown veya UI'da help linki):
  1. SOAR'dan Export for LinkedIn Ads ile CSV indir.
  2. LinkedIn Campaign Manager > Audiences > Create audience > Upload a list.
  3. CSV'yi yükle, eşleşen alanları seç (company name, job title, email vb.).
  4. Bu audience'ı kampanyada hedef kitle olarak seç.

Alan eşlemesi (SOAR → LinkedIn):
- company_name → Company Name
- persona_role / job title → Job Title (veya Job Function)
- address / city / zip → gerekirse Location verisi
- contact (email) varsa → Email (LinkedIn matched audiences için)
Not: LinkedIn bazen sadece email veya sadece company name kabul eder; her iki formatı da destekleyen bir export seçeneği düşün.

---

***REMOVED******REMOVED*** 2) Google Ads + LinkedIn Ads birlikte kullanım

**Amaç:** Aynı SOAR planı/coğrafyası için hem Google Ads hem LinkedIn Ads hedef kitlelerini üretmek veya senkron tutmak. Kullanıcı tek akışta "Google Ads + LinkedIn için export" alabilsin; reklam stratejisi dokümanında iki kanal birlikte nasıl kullanılır kısa özet çıksın.

**İstenenler:**
- Export veya Results Hub'da:
  - "Export for Google Ads" (mevcut veya yeni): Google Ads'in upload formatı (email, phone, address vb. veya Customer Match için gerekli kolonlar).
  - "Export for LinkedIn Ads" (yukarıdaki 1).
  - "Export for Both (Google + LinkedIn)": Tek tıkla iki ayrı CSV veya bir ZIP içinde iki dosya (google_ads_upload.csv, linkedin_ads_upload.csv) + kısa bir "Campaign setup" notu (markdown veya TXT).
- Kısa rehber metni (uygulama içi veya docs):
  - Google Ads + LinkedIn Ads birlikte nasıl kullanılır:
    - Aynı SOAR listesini Google'da Customer Match / Similar Audiences, LinkedIn'de Matched Audiences olarak kullan.
    - Google: reach, arama/display; LinkedIn: meslek/ünvan hedefleme. İkisi birlikte coverage ve frekans artırır.
    - Pratik adımlar: SOAR export > Google Ads Audience upload, SOAR export > LinkedIn Audience upload; aynı kampanya hedefi için iki kanalı aynı listeyle besle.

Teknik:
- Mevcut POST /api/export/results (format: csv, pdf, maps) yapısına yeni formatlar eklenebilir: "linkedin_ads", "google_ads", "both_ads". Veya ayrı endpoint: POST /api/export/audience { format: "linkedin_ads" | "google_ads" | "both", query_id: "..." }.
- CSV kolonları her platformun dokümantasyonuna göre (LinkedIn / Google Ads upload specs) netleştirilsin.
```

---

***REMOVED******REMOVED*** Ek notlar (isteğe bağlı)

- **UPAP / usage-based:** Bu özellikler kullanım (export) sayısına göre faturalandırılıyorsa, "Export for LinkedIn Ads" ve "Export for Both" ayrı birimler olarak sayılabilir; mevcut usage/billing servisine entegre et.
- **Dil:** UI metinleri EN (ve gerekirse TR) olsun; rehber EN yazılabilir.
- **Güvenlik:** Export'lar mevcut yetkilendirme (plan_id / API key) ile sınırlı kalsın; admin panelinden de erişim gerekmiyorsa sadece kullanıcı tarafında kalsın.

```

---

***REMOVED******REMOVED*** Kısa özet (senin yazacağın metin için fikir)

**SOAR'dan çıkan lead'leri LinkedIn Ads kampanyasına birebir nasıl map'lersin:**

1. SOAR Results Hub'dan "Export for LinkedIn Ads" ile CSV indir (şirket adı, persona/ünvan, varsa email).
2. LinkedIn Campaign Manager → Audiences → Create audience → Upload a list.
3. CSV'yi yükle; LinkedIn'in istediği alanlarla eşleştir (Company Name, Job Title, Email).
4. Kampanyada bu audience'ı hedef kitle olarak seç; böylece SOAR lead listesi LinkedIn reklamlarıyla birebir hedeflenir.

**Google Ads + LinkedIn Ads birlikte:** Aynı SOAR listesini hem Google (Customer Match) hem LinkedIn (Matched Audiences) için export edip iki kanalda aynı hedef kitleyi kullan; Google reach + LinkedIn mesleki hedefleme ile coverage artar.

Bu dokümandaki Cursor prompt'unu projede kullanarak agent'ın bu yetenekleri koda ve dokümantasyona eklemesini sağlayabilirsin.
