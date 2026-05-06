***REMOVED*** Git Merge Steps - Complete Resolution

***REMOVED******REMOVED*** Current Situation
- ✅ Local commit: `645c1b7` (auto-start toggle)
- ⚠️ Remote: 37 commits ahead
- ⚠️ Local: 3 commits ahead
- ⚠️ Uncommitted changes in 7 files
- ⚠️ Many untracked documentation files

***REMOVED******REMOVED*** Solution: Commit All + Pull + Push

***REMOVED******REMOVED******REMOVED*** Step 1: Commit All Uncommitted Changes

```powershell
***REMOVED*** Add all modified files
git add backend/src/app.py
git add backend/src/http/v1/public_router.py
git add backend/src/http/v1/support_router.py
git add backend/src/http/v1/webhooks_router.py
git add backend/src/ui/en/soarb2b_home.html
git add backend/src/ui/soarb2b_onboarding_5q.html

***REMOVED*** Handle deleted file
git rm backend/dockerfile

***REMOVED*** Commit
git commit -m "Local changes: language-aware messages, cache fixes, UI updates"
```

**OR (simpler - add everything):**
```powershell
git add -A
git commit -m "Local changes: language-aware messages, cache fixes, UI updates"
```

***REMOVED******REMOVED******REMOVED*** Step 2: Add Important Untracked Files (Optional)

**If you want to include documentation:**
```powershell
git add backend/src/core/messages.py
git add backend/src/middleware/cache_control_middleware.py
git add backend/src/middleware/custom_static_files.py
git add backend/AUTO_START_TOGGLE_FIX_COMPLETE.md
git add backend/HARDCODED_STRINGS_FIX_SUMMARY.md
git commit -m "Add core modules and documentation"
```

**OR skip documentation files for now (they're just docs)**

***REMOVED******REMOVED******REMOVED*** Step 3: Pull with Merge

```powershell
git pull origin main --no-rebase
```

**This will:**
- Fetch remote changes
- Create a merge commit
- May show conflicts if same files were changed

***REMOVED******REMOVED******REMOVED*** Step 4: Resolve Conflicts (If Any)

**If conflicts occur:**
1. Git will list conflicted files
2. Open each file
3. Look for `<<<<<<<`, `=======`, `>>>>>>>`
4. Keep the correct code, remove markers
5. Then:
```powershell
git add .
git commit -m "Resolve merge conflicts"
```

***REMOVED******REMOVED******REMOVED*** Step 5: Push

```powershell
git push origin main
```

---

***REMOVED******REMOVED*** Alternative: Stash Uncommitted Changes

**If you want to save uncommitted changes for later:**
```powershell
***REMOVED*** Stash uncommitted changes
git stash save "Uncommitted changes before merge"

***REMOVED*** Pull
git pull origin main

***REMOVED*** Apply stashed changes back
git stash pop

***REMOVED*** Resolve conflicts if any, then commit
git add .
git commit -m "Apply stashed changes after merge"
git push origin main
```

---

***REMOVED******REMOVED*** Quick Status Check

**After each step, check status:**
```powershell
git status
```

**Check what's different:**
```powershell
git log --oneline --graph --all -10
```

---

***REMOVED******REMOVED*** Recommended: Commit Everything First

**Safest approach:**
```powershell
***REMOVED*** 1. Commit all changes
git add -A
git commit -m "Local changes: auto-start toggle, language-aware messages, cache fixes"

***REMOVED*** 2. Pull
git pull origin main --no-rebase

***REMOVED*** 3. Resolve conflicts if any
***REMOVED*** (edit files, then:)
git add .
git commit -m "Resolve merge conflicts"

***REMOVED*** 4. Push
git push origin main
```
