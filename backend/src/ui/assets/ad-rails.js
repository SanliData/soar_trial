/**
 * SOAR B2B — Kenar dikey reklam alanları (tüm uygulama).
 * Geniş ekranda kenar boşluklarını (gutter) da kullanır:
 * - İçeriğe sağ/sol padding vererek reklamın içerikle çakışmasını engeller
 * - Mobil/tablet'te tamamen gizlenir (kullanıcıyı kasmaz)
 */
(function () {
    if (window.__AD_RAILS_INIT__) return;
    window.__AD_RAILS_INIT__ = true;

    // Layout knobs (safe defaults)
    var RAIL_TOTAL = 220; // rail container width (includes padding)
    var RAIL_INNER = 160; // ad width target
    var RAIL_GAP = 16; // distance from viewport edge

    var style = document.createElement('style');
    style.textContent = [
        ':root { --ad-rail-total: ' + RAIL_TOTAL + 'px; --ad-rail-gap: ' + RAIL_GAP + 'px; }',
        // Reserve gutters so content never sits under rails (desktop only)
        '@media (min-width: 1280px) {',
        '  body { padding-left: calc(var(--ad-rail-total) + var(--ad-rail-gap)); padding-right: calc(var(--ad-rail-total) + var(--ad-rail-gap)); }',
        '}',
        '.ad-rail-left, .ad-rail-right {',
        '  position: fixed; top: 80px; width: var(--ad-rail-total); max-height: 85vh;',
        '  z-index: 8; display: flex; align-items: flex-start; justify-content: center;',
        '  pointer-events: auto; overflow: hidden;',
        '  background: rgba(15, 23, 42, 0.02); border: 1px solid rgba(248, 250, 252, 0.06); border-radius: 8px;',
        '}',
        '.ad-rail-left { left: var(--ad-rail-gap); }',
        '.ad-rail-right { right: var(--ad-rail-gap); }',
        '.ad-rail-left .ad-rail-inner, .ad-rail-right .ad-rail-inner {',
        '  min-height: 600px; width: ' + RAIL_INNER + 'px; text-align: center;',
        '}',
        // Hide rails on < 1280px screens to avoid pressure
        '@media (max-width: 1279px) { body { padding-left: 0 !important; padding-right: 0 !important; } .ad-rail-left, .ad-rail-right { display: none !important; } }',
        '@media (max-height: 600px) { .ad-rail-left, .ad-rail-right { max-height: 70vh; } }'
    ].join('\n');
    document.head.appendChild(style);

    var railLeft = document.createElement('div');
    railLeft.className = 'ad-rail-left';
    railLeft.setAttribute('aria-label', 'Advertisement');
    railLeft.innerHTML = '<div class="ad-rail-inner" id="ad-rail-left-inner"></div>';

    var railRight = document.createElement('div');
    railRight.className = 'ad-rail-right';
    railRight.setAttribute('aria-label', 'Advertisement');
    railRight.innerHTML = '<div class="ad-rail-inner" id="ad-rail-right-inner"></div>';

    document.body.appendChild(railLeft);
    document.body.appendChild(railRight);

    var base = window.API_BASE || window.location.origin + (window.API_BASE_PATH || '');
    fetch(base + '/api/v1/public/ad-config', { credentials: 'same-origin' })
        .then(function (r) { return r.json(); })
        .then(function (c) {
            if (!c.enabled || !c.client_id || !c.slots) return;
            var slotLeft = c.slots['side-left'];
            var slotRight = c.slots['side-right'];
            if (!slotLeft && !slotRight) return;

            function fill(id, slotId) {
                if (!slotId) return;
                var el = document.getElementById(id);
                if (!el) return;
                var ins = document.createElement('ins');
                ins.className = 'adsbygoogle';
                ins.style.display = 'block';
                ins.setAttribute('data-ad-client', c.client_id);
                ins.setAttribute('data-ad-slot', slotId);
                // Keep flexible. Slot itself defines final size; we just provide a vertical-friendly container.
                ins.setAttribute('data-ad-format', 'auto');
                ins.setAttribute('data-full-width-responsive', 'false');
                el.appendChild(ins);
            }
            fill('ad-rail-left-inner', slotLeft);
            fill('ad-rail-right-inner', slotRight);

            if (window.adsbygoogle) (window.adsbygoogle = window.adsbygoogle || []).push({});
            else {
                var s = document.createElement('script');
                s.async = true;
                s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + encodeURIComponent(c.client_id);
                document.head.appendChild(s);
                s.onload = function () { try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {} };
            }
        })
        .catch(function () {});
})();
