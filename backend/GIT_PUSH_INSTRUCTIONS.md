***REMOVED*** Git Push Instructions - Auto-Start Toggle

***REMOVED******REMOVED*** Current Situation
- ✅ Local commit created: `645c1b7`
- ❌ Remote has changes you don't have locally
- Need to pull first, then push

***REMOVED******REMOVED*** Solution: Pull + Push

***REMOVED******REMOVED******REMOVED*** Step 1: Pull from Remote (Merge Strategy)

**In PowerShell (you're already in the right directory):**
```powershell
git pull origin main
```

**If there are conflicts:**
- Git will show which files have conflicts
- You'll need to resolve them manually
- Then: `git add .` and `git commit`

***REMOVED******REMOVED******REMOVED*** Step 2: Push After Pull

**After successful pull:**
```powershell
git push origin main
```

---

***REMOVED******REMOVED*** Alternative: Rebase Strategy (Cleaner History)

**If you prefer rebase (linear history):**
```powershell
git pull --rebase origin main
```

**If conflicts occur:**
1. Resolve conflicts in files
2. `git add .`
3. `git rebase --continue`
4. `git push origin main`

---

***REMOVED******REMOVED*** Quick Check Before Pull

**See what's different:**
```powershell
git fetch origin
git log HEAD..origin/main --oneline
```

**See what files differ:**
```powershell
git diff HEAD origin/main --name-only
```

---

***REMOVED******REMOVED*** After Successful Push

**Verify in Cloud Shell:**
```bash
cd ~/Finder_os
git pull origin main
grep -r "autoStartQueries" backend/src/ui/*/soarb2b_onboarding_5q.html | wc -l
```

**Expected:** `12` (6 files × 2 occurrences)
