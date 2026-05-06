***REMOVED***!/usr/bin/env python3
"""
SOAR B2B CSV → Google Ads Customer Match formatına dönüştürücü.

Girdi CSV: Email, First Name, Last Name, Country, Company sütunları.
Google'ın gereksinimleri: normalize (küçük harf, trim), SHA256 hash (hex).
Çıktı: google_ads_upload.csv
Hatalı/eksik e-postalar atlanır ve terminalde raporlanır.
"""

import csv
import hashlib
import re
import sys
from pathlib import Path


***REMOVED*** Sütun eşlemesi (case-insensitive)
INPUT_COLUMNS = ["email", "first name", "last name", "country", "company"]
OUTPUT_COLUMNS = ["Email", "First Name", "Last Name", "Country", "Company"]


def normalize_for_hashing(value: str) -> str:
    """Google gereksinimi: boşlukları kaldır, küçük harf, baştaki/sondaki boşluk."""
    if value is None or not isinstance(value, str):
        return ""
    return value.strip().lower()


def is_valid_email(email: str) -> bool:
    """Basit e-posta geçerliliği (en az @ ve nokta)."""
    if not email or not isinstance(email, str):
        return False
    email = email.strip()
    if "@" not in email or "." not in email.split("@")[-1]:
        return False
    ***REMOVED*** Çok kısa veya sadece boşluk
    if len(email) < 5:
        return False
    return True


def sha256_hex(value: str) -> str:
    """Değeri UTF-8 ile encode edip SHA256 hash'ini hex (küçük harf) döndür."""
    normalized = normalize_for_hashing(value)
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest().lower()


def find_row_columns(header_row: list) -> dict:
    """CSV header'ından sütun indekslerini bul (case-insensitive)."""
    mapping = {}
    for i, cell in enumerate(header_row):
        key = (cell or "").strip().lower()
        for col in INPUT_COLUMNS:
            if col not in mapping and key == col:
                mapping[col] = i
                break
    return mapping


def main():
    if len(sys.argv) < 2:
        input_path = Path("soarb2b_export.csv")
        print(f"Kullanım: python {Path(__file__).name} <girdi.csv> [cikti.csv]")
        print(f"Örnek:    python {Path(__file__).name} soarb2b_export.csv")
        print(f"Varsayılan girdi: {input_path.absolute()}")
        print(f"Varsayılan çıktı: google_ads_upload.csv")
        print()
    else:
        input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("google_ads_upload.csv")

    if not input_path.exists():
        print(f"HATA: Girdi dosyası bulunamadı: {input_path}")
        sys.exit(1)

    skipped = []
    written = 0

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("HATA: CSV dosyası boş.")
            sys.exit(1)

        col_map = find_row_columns(header)
        if "email" not in col_map:
            print("HATA: CSV'de 'Email' sütunu bulunamadı. Mevcut sütunlar:", header)
            sys.exit(1)

        rows_out = []
        for row_num, row in enumerate(reader, start=2):
            if len(row) <= max(col_map.values()):
                skipped.append((row_num, "Satır çok kısa", row[:3]))
                continue
            email_raw = row[col_map["email"]].strip() if col_map["email"] < len(row) else ""
            if not is_valid_email(email_raw):
                skipped.append((row_num, "Geçersiz veya eksik e-posta", email_raw or "(boş)"))
                continue

            first = row[col_map["first name"]] if "first name" in col_map and col_map["first name"] < len(row) else ""
            last = row[col_map["last name"]] if "last name" in col_map and col_map["last name"] < len(row) else ""
            country = row[col_map["country"]] if "country" in col_map and col_map["country"] < len(row) else ""
            company = row[col_map["company"]] if "company" in col_map and col_map["company"] < len(row) else ""

            rows_out.append({
                "Email": sha256_hex(email_raw),
                "First Name": sha256_hex(first) if first else "",
                "Last Name": sha256_hex(last) if last else "",
                "Country": sha256_hex(country) if country else "",
                "Company": sha256_hex(company) if company else "",
            })
            written += 1

    with open(output_path, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Çıktı: {output_path.absolute()} ({written} satır yazıldı)")
    if skipped:
        print("\n--- Atlanan / hatalı kayıtlar ---")
        for row_num, reason, detail in skipped:
            print(f"  Satır {row_num}: {reason} — {detail}")
        print(f"Toplam atlanan: {len(skipped)}")
    else:
        print("Tüm e-postalar geçerli; atlanan kayıt yok.")


if __name__ == "__main__":
    main()
