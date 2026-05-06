***REMOVED*** Verify SOAR B2B Strategic Hardening

This repository includes a lightweight verification script to validate the strategic hardening pass.

***REMOVED******REMOVED*** Run locally

From the repository root:

```bash
python scripts/verify_soarb2b_hardening.py
```

***REMOVED******REMOVED*** Run against a live server

Linux/macOS (bash):

```bash
VERIFY_BASE_URL=https://soarb2b.com python scripts/verify_soarb2b_hardening.py
```

Windows PowerShell:

```powershell
$env:VERIFY_BASE_URL="https://soarb2b.com"
python scripts/verify_soarb2b_hardening.py
```

***REMOVED******REMOVED*** What it checks

- Required files exist
- MainBook contains **16. Strategic Hardening Backlog**
- LiveBook contains **16. Verification Protocol for Strategic Hardening**
- UTF-8 BOM scan on changed text files
- Obvious secret patterns scan on changed files (placeholders/examples are excluded)
- Optional URL checks (health + static UI paths) if `VERIFY_BASE_URL` is set

