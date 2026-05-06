/**
 * SOAR B2B API → Google Sheets senkronizasyonu
 *
 * - Google Sheets API (google-auth-library) ile kimlik doğrulama
 * - SOAR B2B API'ye GET isteği (yeni şirketler)
 * - Gelen şirketleri (Company Name, Website, Decision Maker Role) sheet'in sonuna ekler
 * - Mükerrer kontrolü: daha önce eklenmiş şirketleri tekrar eklemez
 *
 * Ortam değişkenleri veya .env:
 *   SOARB2B_API_BASE  - Örn: https://soarb2b.com veya http://localhost:9000
 *   SOARB2B_API_KEY   - B2B API anahtarı (X-API-Key)
 *   GOOGLE_SHEETS_CREDENTIALS - Service account JSON dosya yolu (veya GOOGLE_APPLICATION_CREDENTIALS)
 *   GOOGLE_SHEET_ID   - Hedef Google Sheet ID
 */

const { google } = require("googleapis");
const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");

const SOARB2B_API_BASE = process.env.SOARB2B_API_BASE || "https://soarb2b.com";
const SOARB2B_API_KEY = process.env.SOARB2B_API_KEY || "dev-key-12345";
const GOOGLE_SHEET_ID = process.env.GOOGLE_SHEET_ID || "";
const CREDENTIALS_PATH =
  process.env.GOOGLE_SHEETS_CREDENTIALS ||
  process.env.GOOGLE_APPLICATION_CREDENTIALS ||
  path.join(__dirname, "service-account.json");

// SOAR B2B'den şirket listesi çekmek için endpoint (dökümana göre düzeltin)
// Örnek: /api/v1/b2b/plans/{plan_id}/results veya /api/v1/b2b/intelligence/companies
const SOARB2B_INTELLIGENCE_PATH =
  process.env.SOARB2B_INTELLIGENCE_PATH || "/api/v1/b2b/plans/example/results";

function get(url, apiKey) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith("https") ? https : http;
    const req = lib.get(
      url,
      {
        headers: { "X-API-Key": apiKey, Accept: "application/json" },
      },
      (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          try {
            const json = JSON.parse(data);
            resolve(json);
          } catch {
            resolve({ error: data || res.statusCode });
          }
        });
      }
    );
    req.on("error", reject);
    req.setTimeout(15000, () => {
      req.destroy();
      reject(new Error("Request timeout"));
    });
  });
}

/**
 * SOAR B2B yanıtından şirket listesini çıkarır.
 * Farklı response formatlarına uyum: modules[].data, businesses, companies, vb.
 */
function extractCompaniesFromResponse(body) {
  const out = [];
  const push = (name, website, role) => {
    if (name && String(name).trim()) out.push({ companyName: String(name).trim(), website: String(website || "").trim(), decisionMakerRole: String(role || "").trim() });
  };

  if (Array.isArray(body.companies)) {
    body.companies.forEach((c) => push(c.company_name || c.name || c.companyName, c.website, c.decision_maker_role || c.role || c.title));
    return out;
  }
  if (Array.isArray(body.businesses)) {
    body.businesses.forEach((b) => push(b.name || b.company_name, b.website, b.role || b.job_title));
    return out;
  }
  if (Array.isArray(body.modules)) {
    body.modules.forEach((m) => {
      const data = m.data || m.results || m.items || [];
      (Array.isArray(data) ? data : []).forEach((row) => {
        const name = row.company_name || row.name || row.companyName;
        const web = row.website;
        const role = row.decision_maker_role || row.role || row.job_title || row.title;
        push(name, web, role);
      });
    });
    return out;
  }
  if (Array.isArray(body)) {
    body.forEach((row) => push(row.company_name || row.name, row.website, row.decision_maker_role || row.role || row.title));
    return out;
  }
  return out;
}

async function fetchSoarB2BCompanies() {
  const url = SOARB2B_API_BASE.replace(/\/$/, "") + SOARB2B_INTELLIGENCE_PATH;
  const body = await get(url, SOARB2B_API_KEY);
  if (body.error) throw new Error("SOAR B2B API error: " + (body.error.message || body.error));
  return extractCompaniesFromResponse(body);
}

async function getSheetsClient() {
  const credPath = path.isAbsolute(CREDENTIALS_PATH) ? CREDENTIALS_PATH : path.join(__dirname, CREDENTIALS_PATH);
  if (!fs.existsSync(credPath)) {
    throw new Error("Google credentials not found at: " + credPath + "\nSet GOOGLE_SHEETS_CREDENTIALS or add service-account.json");
  }
  const auth = new google.auth.GoogleAuth({
    keyFile: credPath,
    scopes: ["https://www.googleapis.com/auth/spreadsheets"],
  });
  const sheets = google.sheets({ version: "v4", auth });
  return sheets;
}

async function getExistingRows(sheets, sheetId, range) {
  try {
    const res = await sheets.spreadsheets.values.get({ spreadsheetId: sheetId, range });
    return (res.data.values || []).map((row) => (row[0] || "").trim().toLowerCase());
  } catch (e) {
    if (e.code === 404 || (e.message && e.message.includes("Unable to parse range"))) return [];
    throw e;
  }
}

async function appendRows(sheets, sheetId, rows, range = "Sheet1") {
  if (rows.length === 0) return;
  await sheets.spreadsheets.values.append({
    spreadsheetId: sheetId,
    range: range + "!A:C",
    valueInputOption: "USER_ENTERED",
    insertDataOption: "INSERT_ROWS",
    resource: { values: rows },
  });
}

async function main() {
  if (!GOOGLE_SHEET_ID) {
    console.error("GOOGLE_SHEET_ID ortam değişkeni gerekli (hedef Google Sheet ID).");
    process.exit(1);
  }

  console.log("SOAR B2B'den şirketler çekiliyor...");
  const companies = await fetchSoarB2BCompanies();
  console.log("Bulunan şirket sayısı:", companies.length);

  const sheets = await getSheetsClient();
  const headerRange = "Sheet1!A1:C1";
  const dataRange = "Sheet1!A2:C";

  let existingKeys = await getExistingRows(sheets, GOOGLE_SHEET_ID, dataRange);
  const headerRow = await sheets.spreadsheets.values.get({ spreadsheetId: GOOGLE_SHEET_ID, range: headerRange }).catch(() => ({ data: { values: [] } }));
  const hasHeader = (headerRow.data.values || []).length > 0;
  if (!hasHeader) {
    await sheets.spreadsheets.values.update({
      spreadsheetId: GOOGLE_SHEET_ID,
      range: headerRange,
      valueInputOption: "USER_ENTERED",
      resource: { values: [["Company Name", "Website", "Decision Maker Role"]] },
    });
  }
  if (existingKeys.length === 0 && hasHeader) {
    existingKeys = await getExistingRows(sheets, GOOGLE_SHEET_ID, dataRange);
  }

  const seen = new Set(existingKeys);
  const toAdd = [];
  for (const c of companies) {
    const key = (c.companyName || "").toLowerCase();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    toAdd.push([c.companyName, c.website || "", c.decisionMakerRole || ""]);
  }

  if (toAdd.length === 0) {
    console.log("Eklenecek yeni şirket yok (hepsi zaten mevcut veya mükerrer atlandı).");
    return;
  }

  await appendRows(sheets, GOOGLE_SHEET_ID, toAdd);
  console.log("Google Sheets'e eklenen yeni satır sayısı:", toAdd.length);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
