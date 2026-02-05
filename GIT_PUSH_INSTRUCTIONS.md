# 🚀 Git Push Instructions

## Prerequisites
- Git must be installed on your system
- You must have a GitHub repository set up
- You should be in the project directory

---

## Step-by-Step Git Commands

### 1. Open PowerShell or Command Prompt
Navigate to your project:
```powershell
cd "C:\Users\annap\Desktop\Projects\finished-projects\Digital Twin–Based Railway"
```

---

### 2. Check Git Status
See what files have changed:
```powershell
git status
```

---

### 3. Add All Changes
Add all modified and new files:
```powershell
git add .
```

**OR** add specific files only:
```powershell
git add dashboard/app.py
git add src/utils/simple_platform_tracker.py
git add data/schedules_optimized.csv
git add README.md
git add QUICKSTART.md
```

---

### 4. Commit Changes
Create a commit with a descriptive message:
```powershell
git commit -m "Optimize dashboard: Add platform tracking, fix analytics, convert JSON to CSV"
```

**Alternative detailed commit message:**
```powershell
git commit -m "Major dashboard optimization and feature additions

- Added real-time platform tracking with time-based occupancy
- Fixed Analytics section to show real data instead of static values
- Converted 80MB schedules.json to optimized CSV (32MB)
- Replaced time slider with event-based time selector
- Removed test files and unnecessary data files
- Improved loading performance with disabled auto-load"
```

---

### 5. Push to GitHub
Push to your main branch:
```powershell
git push origin main
```

**OR** if your branch is named `master`:
```powershell
git push origin master
```

**If this is your first push:**
```powershell
git push -u origin main
```

---

## Common Issues & Solutions

### Issue 1: "fatal: not a git repository"
**Solution:** Initialize git first:
```powershell
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Issue 2: "Updates were rejected"
**Solution:** Pull first, then push:
```powershell
git pull origin main --rebase
git push origin main
```

### Issue 3: Large file warning (schedules_optimized.csv)
**Solution:** The CSV is 32MB which is fine for GitHub. If you get an error, you can:
1. Add it to `.gitignore` if you don't want to push it
2. Use Git LFS (Large File Storage) for files >50MB

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `git status` | Check what's changed |
| `git add .` | Stage all changes |
| `git commit -m "message"` | Commit with message |
| `git push origin main` | Push to GitHub |
| `git log --oneline` | View commit history |
| `git diff` | See changes before committing |

---

## Verify Push Success

After pushing, check:
1. Go to your GitHub repository in a browser
2. Verify files are updated
3. Check the commit message appears correctly
4. Confirm the timestamp is recent

---

## 🎉 Done!
Your Railway Digital Twin project is now pushed to GitHub!
