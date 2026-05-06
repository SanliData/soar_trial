***REMOVED***!/bin/bash
***REMOVED*** Cloudflare SSL + Nginx kontrolü - Droplet'te çalıştırın: ./backend/scripts/cloudflare_ssl_check.sh
***REMOVED*** SSH: ssh root@165.227.74.248 (veya kendi IP'niz)

set -e

echo "=========================================="
echo "1. Port 443 (HTTPS) dinleniyor mu?"
echo "=========================================="
ss -tulnp | grep 443 || echo "(bos - 443 yok, Cloudflare Flexible kullanin)"
echo ""

echo "=========================================="
echo "2. Port 8000 (Python) nerede dinliyor?"
echo "=========================================="
ss -tulnp | grep 8000 || echo "(8000 yok)"
echo ""

echo "=========================================="
echo "3. curl http://165.227.74.248 (public IP)"
echo "=========================================="
curl -v -s -o /dev/null -w "HTTP %{http_code}\n" --connect-timeout 5 http://165.227.74.248 || echo "HATA veya timeout"
echo ""

echo "=========================================="
echo "4. curl http://127.0.0.1 (localhost)"
echo "=========================================="
curl -v -s -o /dev/null -w "HTTP %{http_code}\n" --connect-timeout 2 http://127.0.0.1 || echo "HATA"
echo ""

echo "=========================================="
echo "5. Nginx durumu"
echo "=========================================="
systemctl is-active nginx 2>/dev/null || echo "nginx status unknown"
echo ""

echo "--- Cloudflare panelde kontrol edin: SSL/TLS -> Overview -> Mode (Flexible/Full/Full strict) ---"
