***REMOVED***!/bin/bash
***REMOVED*** UPDATE_APP_PY_CLOUDSHELL.sh
***REMOVED*** PURPOSE: Update app.py to use NoCacheStaticFiles in Cloud Shell
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

APP_PY="${BACKEND_DIR}/src/app.py"

echo "📁 Backend directory: ${BACKEND_DIR}"
echo "📁 App.py: ${APP_PY}"
echo ""

***REMOVED*** Check if app.py exists
if [ ! -f "${APP_PY}" ]; then
    echo "❌ app.py not found!"
    exit 1
fi

***REMOVED*** Check if already updated
if grep -q "NoCacheStaticFiles" "${APP_PY}"; then
    echo "✅ app.py already uses NoCacheStaticFiles"
    exit 0
fi

***REMOVED*** Backup
cp "${APP_PY}" "${APP_PY}.backup"
echo "✅ Backup created: ${APP_PY}.backup"
echo ""

***REMOVED*** Add import if not present
if ! grep -q "from src.middleware.custom_static_files import NoCacheStaticFiles" "${APP_PY}"; then
    ***REMOVED*** Add import after StaticFiles import
    sed -i '/from fastapi.staticfiles import StaticFiles/a from src.middleware.custom_static_files import NoCacheStaticFiles' "${APP_PY}"
    echo "✅ Added import"
fi

***REMOVED*** Replace StaticFiles with NoCacheStaticFiles in mount
sed -i 's/app.mount("\/ui", StaticFiles(/app.mount("\/ui", NoCacheStaticFiles(/g' "${APP_PY}"
echo "✅ Updated mount to use NoCacheStaticFiles"
echo ""

***REMOVED*** Verify
if grep -q "NoCacheStaticFiles" "${APP_PY}"; then
    echo "✅ app.py updated successfully!"
    echo ""
    echo "📋 Relevant lines:"
    grep -A 2 -B 2 "NoCacheStaticFiles" "${APP_PY}" | head -n 10
else
    echo "❌ Failed to update app.py!"
    echo "Restoring backup..."
    mv "${APP_PY}.backup" "${APP_PY}"
    exit 1
fi

echo ""
echo "✅ Ready to deploy!"
