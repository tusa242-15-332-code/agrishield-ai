# Deploy AgriShield AI for free (no VS Code)

This package is configured as one Docker web service: FastAPI serves both the API and the React website. Render will assign a public `onrender.com` subdomain.

## Browser-only deployment

1. Sign in or create a GitHub account at https://github.com
2. Create a repository named `agrishield-ai`.
3. In the repository choose **Add file → Upload files**.
4. Extract this ZIP on your computer. Open the extracted `agrishield-deploy` folder and upload all its contents (including `Dockerfile` and `render.yaml`) to GitHub. Commit the upload.
5. Sign in at https://render.com.
6. Choose **New + → Web Service**, connect GitHub and select the `agrishield-ai` repository.
7. Use Docker runtime / `./Dockerfile` if Render does not automatically detect the included `render.yaml`.
8. Select the Free instance and deploy.
9. When deployment completes, open the generated `https://<service-name>.onrender.com` address.
10. Verify `/api/health` and `/docs` on the same domain.

## Free-tier limitations

- Render free web services spin down after 15 minutes without incoming traffic. The first visit after sleeping may take about a minute to wake.
- Free services are suitable for demos and testing, not production-critical services.
- Marketplace listings and activity currently live in process memory and may reset after a restart/redeploy.
- This MVP does not yet include user authentication, persistent PostgreSQL, real payments, a trained disease classifier, or a validated ML climate model.
- Never commit secret keys to the public repository.

If deployment fails, open Render → service → Logs and share the first real error message.
