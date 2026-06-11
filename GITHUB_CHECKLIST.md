# GitHub Upload Checklist

This document lists all changes made to prepare your repo for GitHub and what you need to do next.

---

## ✅ Files Created (Safe to Push)

These new files have been created and are **safe to commit to Git**:

1. **`services/auth/.env.example`** - Template env file with placeholder values
2. **`infra/docker-compose.example.yml`** - Template Docker Compose with environment variables
3. **`SETUP.md`** - Developer setup guide (this repo's root)

### Files Modified (Safe to Push)

1. **`.gitignore`** - Updated to:
   - Explicitly exclude `authvenv/` and other service venvs
   - Exclude `docker-compose.yml` (but not `.example` versions)
   - Exclude `.env` files (but not `.example` versions)

2. **`testfolder/producer.py`** - Updated to:
   - Load RabbitMQ credentials from environment variables
   - No longer contains hardcoded username/password

3. **`testfolder/consumer.py`** - Updated to:
   - Load RabbitMQ credentials from environment variables
   - No longer contains hardcoded username/password

---

## ⚠️ Files NOT to Push (Must Remove from Git Tracking)

These files exist but should **never** be committed to GitHub:

1. **`services/auth/.env`** - Contains real secrets
2. **`infra/docker-compose.yml`** - Contains real passwords
3. **`services/auth/authvenv/`** - Local Python virtual environment

### How to Remove Them from Git

Run these commands in your repository root:

```powershell
# Stop tracking .env file (keeps it locally)
git rm --cached services/auth/.env

# Stop tracking docker-compose.yml
git rm --cached infra/docker-compose.yml

# Stop tracking virtual environment
git rm -r --cached services/auth/authvenv

# Add/commit the .gitignore changes
git add .gitignore
git commit -m "Update .gitignore to exclude secrets and venv directories"
```

---

## 📋 Safe to Push (All Application Code)

These directories and files are **safe to commit**:

- ✅ `services/auth/app/` - All application source code
- ✅ `services/auth/tests/` - Test files (no real secrets)
- ✅ `services/auth/migrations/` - Database migrations
- ✅ `services/auth/requirements.txt` - Python dependencies
- ✅ `services/auth/Dockerfile` - Docker build instructions
- ✅ `services/auth/conftest.py` - Test configuration
- ✅ `services/auth/alembic.ini` - Alembic configuration
- ✅ `testfolder/producer.py` - Updated (no hardcoded secrets)
- ✅ `testfolder/consumer.py` - Updated (no hardcoded secrets)
- ✅ `README.md` - Documentation
- ✅ `LICENSE` - License file
- ✅ `frontend/` - Frontend code
- ✅ `images/` - Image assets
- ✅ All other service files

---

## 🚀 Final Steps Before Pushing

1. **Verify nothing sensitive is staged:**
   ```powershell
   git status
   git diff --cached | Select-String -Pattern "password|secret|token|key" -ErrorAction SilentlyContinue
   ```

2. **Remove tracked sensitive files:**
   ```powershell
   git rm --cached services/auth/.env
   git rm --cached infra/docker-compose.yml
   git rm -r --cached services/auth/authvenv
   ```

3. **Commit the cleanup:**
   ```powershell
   git add .gitignore
   git commit -m "Remove secrets and venv from git tracking"
   ```

4. **Verify .gitignore works for future changes:**
   ```powershell
   # Create test files to verify they're ignored
   echo "test" > services/auth/.env.test
   echo "test" > infra/docker-compose.test.yml
   
   git status  # These should not appear as untracked
   
   # Clean up test files
   Remove-Item services/auth/.env.test
   Remove-Item infra/docker-compose.test.yml
   ```

5. **Push to GitHub:**
   ```powershell
   git push origin main
   ```

---

## 📖 Documentation

- **SETUP.md** - How to set up the project locally
- **README.md** - General project information
- **.env.example** - What environment variables to set
- **docker-compose.example.yml** - How to configure Docker services

---

## Security Checklist

Before pushing, verify:

- [ ] `.env` file is not in git (only `.env.example` is)
- [ ] `docker-compose.yml` is not in git (only `docker-compose.example.yml` is)
- [ ] `authvenv/` is not in git
- [ ] No hardcoded passwords in Python files
- [ ] No API keys or secrets in any `.py` files
- [ ] `.gitignore` is updated and committed
- [ ] All new files pass a final review with `git diff --cached`

---

## If You've Already Committed Secrets

If you accidentally committed `.env` or passwords before, they're still in Git history.
You must:

1. **Rotate all secrets** (generate new JWT keys, database passwords, etc.)
2. **Clean Git history** (use `git filter-branch` or `BFG Repo-Cleaner`)
3. **Force push** (only if the repo is private or you control all access)

See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

---

## Summary

- ✅ Created safe template files (`.env.example`, `docker-compose.example.yml`)
- ✅ Updated test scripts to use environment variables
- ✅ Updated `.gitignore` to exclude secrets and venv
- ⚠️ **Next step:** Remove `.env`, `docker-compose.yml`, and `authvenv/` from git tracking
- 🚀 **Then:** Commit and push to GitHub

Run the commands in the **Final Steps** section above to complete the cleanup.
