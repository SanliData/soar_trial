***REMOVED***!/bin/bash
***REMOVED*** CREATE_CUSTOM_STATICFILES_CLOUDSHELL.sh
***REMOVED*** PURPOSE: Create custom_static_files.py in Cloud Shell
***REMOVED*** ENCODING: UTF-8 WITHOUT BOM

BACKEND_DIR=""
if [ -d ~/Finder_os/backend ]; then
    BACKEND_DIR=~/Finder_os/backend
elif [ -d ~/FINDER_OS/backend ]; then
    BACKEND_DIR=~/FINDER_OS/backend
else
    echo "❌ Backend directory not found!"
    exit 1
fi

MIDDLEWARE_DIR="${BACKEND_DIR}/src/middleware"

echo "📁 Backend directory: ${BACKEND_DIR}"
echo "📁 Middleware directory: ${MIDDLEWARE_DIR}"
echo ""

***REMOVED*** Create middleware directory if it doesn't exist
mkdir -p "${MIDDLEWARE_DIR}"

***REMOVED*** Create custom_static_files.py
cat > "${MIDDLEWARE_DIR}/custom_static_files.py" << 'EOF'
"""
CUSTOM_STATIC_FILES: Custom StaticFiles with cache headers
PURPOSE: StaticFiles subclass that forces no-cache headers for HTML files
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi.staticfiles import StaticFiles
from starlette.responses import Response


class NoCacheStaticFiles(StaticFiles):
    """
    Custom StaticFiles that adds no-cache headers to HTML files.
    Overrides get_response to modify headers before response is sent.
    """
    
    async def get_response(self, path: str, scope):
        """
        Override get_response to add cache headers for HTML files.
        """
        response = await super().get_response(path, scope)
        
        ***REMOVED*** Check if this is an HTML file
        is_html = (
            path.lower().endswith('.html') or
            path.lower().startswith('/ui/') or
            response.headers.get('content-type', '').startswith('text/html')
        )
        
        if is_html:
            ***REMOVED*** Add cache headers
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers["CDN-Cache-Control"] = "no-cache"
            
            ***REMOVED*** Remove ETag and Last-Modified (prevent conditional requests)
            if "ETag" in response.headers:
                del response.headers["ETag"]
            if "Last-Modified" in response.headers:
                del response.headers["Last-Modified"]
        
        return response
EOF

echo "✅ Created: ${MIDDLEWARE_DIR}/custom_static_files.py"
echo ""

***REMOVED*** Verify
if [ -f "${MIDDLEWARE_DIR}/custom_static_files.py" ]; then
    echo "✅ File created successfully!"
    echo ""
    echo "📋 File content (first 10 lines):"
    head -n 10 "${MIDDLEWARE_DIR}/custom_static_files.py"
else
    echo "❌ Failed to create file!"
    exit 1
fi

echo ""
echo "✅ Ready to deploy!"
echo ""
