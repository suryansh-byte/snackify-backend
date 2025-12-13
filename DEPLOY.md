Deployment guide — prepare and push to GitHub, then deploy to Render

This file explains how to push the `SNACKIFY` backend to GitHub and deploy it on Render (recommended).

1) Cleanup before pushing
- Remove local sqlite DB from git index if present (it may already be committed). Run these commands in the `SNACKIFY` folder:

```powershell
cd 'C:\Users\KIIT\New folder\SNACKIFY'
# Ensure .gitignore contains 'instance/' and '*.db' entries (we added .gitignore earlier)
# If the DB is already committed, remove it from the index:
if (Test-Path 'instance/snackify.db') { git rm --cached instance/snackify.db; git commit -m "Remove local DB from index" }
```

2) Create a remote GitHub repository
- On GitHub create a new repo (e.g. `snackify-backend`) under your account or organization.
- Alternatively, from PowerShell (you'll need a PAT):

```powershell
# create remote and push (replace <GITHUB_REMOTE_URL> with the repo URL)
git remote add origin https://github.com/<YOUR_GITHUB_USER>/snackify-backend.git
git branch -M main
git push -u origin main
```

3) Connect to Render (recommended)
- Go to https://dashboard.render.com and create an account (if you don't have one).
- Click "New" → "Web Service" → Connect your GitHub repo and choose the `snackify-backend` repo.
- Choose branch: `main`.
- Build command: leave empty (Render will build using Dockerfile) or set to `pip install -r requirements.txt`.
- Start command: `gunicorn app:app --bind 0.0.0.0:${PORT} --workers 2`.
- Render will build and deploy; it returns a live URL like `https://snackify-backend.onrender.com`.

4) Environment variables
- In Render dashboard, set environment variables if needed (e.g., `DATABASE_URL`, `SECRET_KEY`). For quick testing you can keep defaults — the app uses `sqlite:///snackify.db` by default.

5) Verify after deployment
- Open the Render service URL and call `/health`:

```powershell
Invoke-RestMethod -Uri https://<YOUR_SERVICE>.onrender.com/health -Method GET
```

6) GitHub Actions (optional)
- We added a basic CI workflow at `.github/workflows/ci.yml` that installs deps on push.
- To auto-deploy via GitHub Actions you can add a deploy step that calls Render's API using a Render API key stored in GitHub Secrets. See Render docs for `render-deploy` usage.

7) If you prefer I can do the GitHub + Render steps for you (requires tokens). Otherwise push and connect Render and paste the live URL here and I'll verify everything and help wire the Flutter app.

If anything fails during your push/deploy, paste the build logs here and I'll help fix them.

8) (Optional) Connect a MongoDB Atlas cluster and seed demo data

- Create a MongoDB Atlas cluster (free tier is fine) and get the connection string (URI). It looks like:

```
mongodb+srv://<user>:<password>@cluster0.abcd.mongodb.net/snackify?retryWrites=true&w=majority
```

- In the Render dashboard for your service, add an environment variable named `MONGODB_URI` and paste the full URI value.

- Ensure `requirements.txt` includes `pymongo` and `dnspython` (already added). When Render rebuilds, the app will attempt to connect to MongoDB on startup.

- To seed demo data (users, restaurants, drivers) you can run the provided `seed_mongo.py` locally against your Atlas cluster. Example (PowerShell):

```powershell
cd 'C:\Users\KIIT\New folder\SNACKIFY'
$env:MONGODB_URI = 'mongodb+srv://<user>:<password>@cluster0.abcd.mongodb.net/snackify?retryWrites=true&w=majority'
python seed_mongo.py
```

This will insert example documents into the database referenced by `MONGODB_URI`. After seeding, call the `/mongo-health` endpoint on your Render service to verify connectivity:

```powershell
Invoke-RestMethod -Uri https://<YOUR_SERVICE>.onrender.com/mongo-health -Method GET
```

Notes:
- The app is backward-compatible — if `MONGODB_URI` is not set, the SQLAlchemy/SQLite flow remains active.
- If you want me to seed the MongoDB for you, provide the `MONGODB_URI` and I can run the seeding step and verify `/mongo-health` for you.
