// op_surface_helpers.js
// PURPOSE: Small deterministic helpers for Phase 2 surfaces (no streaming)
// ENCODING: UTF-8 WITHOUT BOM

export async function getJson(url, fallback) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("http " + res.status);
    return await res.json();
  } catch (e) {
    return fallback;
  }
}

export function escapeHtml(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&***REMOVED***039;");
}

export function setDot(el, level) {
  const cls = (level === "ok") ? "ok" : (level === "warn") ? "warn" : (level === "crit") ? "crit" : "";
  el.innerHTML = `<span class="op-dot ${cls}"></span><span>${escapeHtml(el.dataset.label || "")}</span>`;
}

