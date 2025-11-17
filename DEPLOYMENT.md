# Deployment Guide - Streamlit Community Cloud

## Quick Deploy (5 minutes)

### Step 1: Sign In to Streamlit Community Cloud
1. Go to https://share.streamlit.io/
2. Click "Sign in with GitHub"
3. Authorize Streamlit to access your GitHub account

### Step 2: Deploy Your App
1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository**: `madakas/forbes500-rto-dashboard`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (custom): Choose your preferred subdomain (e.g., `forbes500-rto`)

3. Click **"Deploy!"**

### Step 3: Wait for Deployment
- Initial deployment takes 2-5 minutes
- Streamlit will install dependencies from `requirements.txt`
- Once complete, your app will be live at: `https://[your-app-name].streamlit.app`

## Post-Deployment

### Automatic Updates
- Every time you push to the `main` branch, the app auto-updates
- No manual redeployment needed
- Changes typically reflect within 1-2 minutes

### Managing Your App
Access your app dashboard at https://share.streamlit.io/ to:
- View logs
- Reboot the app
- Check resource usage
- Manage settings
- Delete the app

### Updating Data
To add new research batches:

1. Add new batch files to the original research directory
2. Run the merge script:
```bash
cd forbes500-rto-dashboard
python3 utils/merge_data.py
```

3. Commit and push:
```bash
git add data/forbes500_rto_data.json
git commit -m "Update: Add new research batch"
git push
```

4. App will auto-update within 1-2 minutes

## Troubleshooting

### App Not Loading
- Check the logs in the Streamlit Cloud dashboard
- Verify all files are committed and pushed to GitHub
- Ensure `requirements.txt` has correct dependencies

### Resource Limits Exceeded
Free tier limits:
- 1 GB RAM
- 1 CPU core
- Apps sleep after 7 days of inactivity

If you hit limits:
- Optimize data loading with `@st.cache_data`
- Reduce data file size
- Consider upgrading to Streamlit Cloud Pro

### Data Not Updating
- Clear cache: Click "Clear cache" in the app menu (⋮)
- Or force refresh: Press `C` while viewing the app
- Or programmatically: Update the `load_data()` function

## Custom Domain (Optional)

To use your own domain:
1. Upgrade to Streamlit Cloud Pro
2. Follow the custom domain setup guide
3. Point your DNS to Streamlit's servers

## Testing Locally Before Deploy

```bash
# Test locally first
streamlit run app.py

# View at http://localhost:8501
# Check for errors before deploying
```

## Environment Variables (If Needed)

If you need to add API keys or secrets:
1. Go to app settings in Streamlit Cloud
2. Click "Secrets"
3. Add in TOML format:
```toml
# Example (not needed for current app)
API_KEY = "your-key-here"
```

## Links
- **App Dashboard**: https://share.streamlit.io/
- **Documentation**: https://docs.streamlit.io/deploy/streamlit-community-cloud
- **Support**: https://discuss.streamlit.io/

---

**Your App URL**: `https://[your-chosen-name].streamlit.app`

**GitHub Repo**: https://github.com/madakas/forbes500-rto-dashboard
