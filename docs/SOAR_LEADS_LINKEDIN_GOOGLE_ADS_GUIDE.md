***REMOVED*** SOAR lead'lerini LinkedIn Ads ve Google Ads'e aktarma

***REMOVED******REMOVED*** 1) SOAR lead'lerini LinkedIn Ads kampanyasına birebir map'leme

1. **SOAR Results Hub** sayfasında "Export for LinkedIn Ads" (veya "LinkedIn Ads için dışa aktar") ile CSV indir. Dosyada: Company Name, Job Title (persona role), Address, City, ZIP ve boş alanlar (First Name, Last Name, Email) bulunur.
2. **LinkedIn Campaign Manager** > **Audiences** > **Create audience** > **Upload a list**.
3. CSV'yi yükle; LinkedIn'in istediği alanlarla eşleştir (Company Name, Job Title vb.). Email / First / Last Name eklediğiniz veriler varsa onları da eşleştirin.
4. Bu audience'ı kampanyada **hedef kitle** olarak seçin. SOAR listesi LinkedIn reklamlarıyla birebir hedeflenir.

**Alan eşlemesi (SOAR → LinkedIn):**
- `company_name` → Company Name  
- `persona_role` → Job Title (veya Job Function)  
- `address`, `city`, `zip` → Adres / lokasyon  
- İleride contact (email) eklerseniz → Email (Matched Audiences için)

---

***REMOVED******REMOVED*** 2) Google Ads + LinkedIn Ads birlikte kullanım

- **Export for Google Ads:** Google Ads Customer Match için uygun CSV (Email, Phone, First/Last Name, City, State, ZIP, Country, Company Name, Address). SOAR’da email/telefon yoksa ilgili kolonlar boş; adres/şirket ile de eşleşme kullanılabilir.
- **Export for Both (Google + LinkedIn):** Tek ZIP içinde `linkedin_ads_upload_*.csv`, `google_ads_upload_*.csv` ve `campaign_setup.txt` (kısa kampanya kurulum notu).

**Pratik kullanım:**
- Aynı SOAR listesini **Google’da** Customer Match / Similar Audiences, **LinkedIn’de** Matched Audiences olarak kullanın.
- Google: erişim, arama/display; LinkedIn: mesleki/ünvan hedefleme. İkisi birlikte kapsam ve frekansı artırır.
- Adımlar: SOAR’dan export alın > Google Ads’te Audience yükleyin, SOAR’dan export alın > LinkedIn’de Audience yükleyin; aynı kampanya hedefi için iki kanalı aynı listeyle besleyin.
