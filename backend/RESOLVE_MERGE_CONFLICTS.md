***REMOVED*** Resolve Merge Conflicts - Strategy

***REMOVED******REMOVED*** Critical Conflicts (Auto-Start Toggle)

**These files MUST keep our auto-start toggle:**
- `backend/src/ui/en/soarb2b_onboarding_5q.html`
- `backend/src/ui/tr/soarb2b_onboarding_5q.html`
- `backend/src/ui/de/soarb2b_onboarding_5q.html`
- `backend/src/ui/es/soarb2b_onboarding_5q.html`
- `backend/src/ui/fr/soarb2b_onboarding_5q.html`
- `backend/src/ui/ar/soarb2b_onboarding_5q.html`
- `backend/src/ui/soarb2b_onboarding_5q.html`

***REMOVED******REMOVED*** Strategy

***REMOVED******REMOVED******REMOVED*** Option 1: Accept Our Version (Auto-Start Toggle)

**For onboarding files (keep our changes):**
```powershell
***REMOVED*** Accept our version for onboarding files
git checkout --ours backend/src/ui/en/soarb2b_onboarding_5q.html
git checkout --ours backend/src/ui/tr/soarb2b_onboarding_5q.html
git checkout --ours backend/src/ui/de/soarb2b_onboarding_5q.html
git checkout --ours backend/src/ui/es/soarb2b_onboarding_5q.html
git checkout --ours backend/src/ui/fr/soarb2b_onboarding_5q.html
git checkout --ours backend/src/ui/ar/soarb2b_onboarding_5q.html
git checkout --ours backend/src/ui/soarb2b_onboarding_5q.html
```

***REMOVED******REMOVED******REMOVED*** Option 2: Accept Remote Version (Then Re-apply Auto-Start)

**If remote has important changes:**
```powershell
***REMOVED*** Accept remote version
git checkout --theirs backend/src/ui/en/soarb2b_onboarding_5q.html
***REMOVED*** Then manually add auto-start toggle back
```

***REMOVED******REMOVED******REMOVED*** Option 3: Manual Merge (Recommended for Critical Files)

**For onboarding files, manually resolve:**
1. Open conflicted file
2. Find `<<<<<<<`, `=======`, `>>>>>>>` markers
3. Keep auto-start toggle section (our changes)
4. Keep other remote changes
5. Remove conflict markers

***REMOVED******REMOVED*** Quick Resolution Commands

***REMOVED******REMOVED******REMOVED*** Step 1: Accept Our Version for Onboarding Files

```powershell
***REMOVED*** Keep our auto-start toggle changes
git checkout --ours backend/src/ui/*/soarb2b_onboarding_5q.html
git checkout --ours backend/src/ui/soarb2b_onboarding_5q.html
```

***REMOVED******REMOVED******REMOVED*** Step 2: Accept Remote Version for Other Files (or resolve manually)

```powershell
***REMOVED*** For non-critical files, accept remote
git checkout --theirs ABOUT_FINDEROS.md
git checkout --theirs PRE_DEPLOYMENT_CHECK.ps1
git checkout --theirs TEST_MULTILINGUAL_FRONTEND.ps1
git checkout --theirs backend/requirements.txt
git checkout --theirs backend/src/models/usage_billing_event.py
```

***REMOVED******REMOVED******REMOVED*** Step 3: For UI Home Files, Check What Changed

```powershell
***REMOVED*** See what's different
git diff --ours backend/src/ui/en/soarb2b_home.html
git diff --theirs backend/src/ui/en/soarb2b_home.html
```

**Then decide:**
- If remote has important changes: `git checkout --theirs`
- If our changes are important: `git checkout --ours`
- If both: resolve manually

***REMOVED******REMOVED******REMOVED*** Step 4: Add All Resolved Files

```powershell
git add .
```

***REMOVED******REMOVED******REMOVED*** Step 5: Complete Merge

```powershell
git commit -m "Resolve merge conflicts: keep auto-start toggle, merge remote changes"
```

***REMOVED******REMOVED******REMOVED*** Step 6: Push

```powershell
git push origin main
```

---

***REMOVED******REMOVED*** Verify Auto-Start Toggle After Merge

```powershell
***REMOVED*** Check that auto-start toggle still exists
grep -r "autoStartQueries" backend/src/ui/*/soarb2b_onboarding_5q.html
```

**Expected:** 12 lines (6 files × 2 occurrences)

---

***REMOVED******REMOVED*** Alternative: Abort and Use Rebase

**If conflicts are too complex:**
```powershell
***REMOVED*** Abort merge
git merge --abort

***REMOVED*** Use rebase instead (cleaner history)
git pull --rebase origin main

***REMOVED*** Resolve conflicts one by one
***REMOVED*** After each conflict: git add . && git rebase --continue
```
