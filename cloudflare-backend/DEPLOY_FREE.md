# ExamForge AI - 100% Free Cloudflare Stack Deployment Guide

This guide shows you how to deploy your ExamForge AI website and backend **completely free forever** using the tools in your screenshot:
1. **GitHub** (Code repository)
2. **Cloudflare Pages** (Free frontend hosting for `index.html` with custom domain `alibuild.site`)
3. **Cloudflare Workers** (Free global serverless API - replaces localhost FastAPI)
4. **Cloudflare D1** (Free serverless SQLite database - replaces local `examforge.db`)
5. **Gemini / Groq API** (Free AI paper question generator)

---

## Why This Solves The "Other Device Cannot Login" Problem Forever

- **Before:** The FastAPI backend ran on your computer (`http://localhost:8000`). Other phones and devices could not access your computer's `localhost`.
- **With Cloudflare Workers + D1:** The backend runs at `https://examforge-api.<your-subdomain>.workers.dev`. It is live 24/7 in the cloud with free HTTPS. Any school on any mobile phone, laptop, or tablet in the world can log in immediately!

---

## Method 1: Deploy Worker in 2 Minutes via Cloudflare Dashboard (No CLI needed)

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. In the left sidebar, click **Compute (Workers & Pages)** -> **Workers** -> **Create Application**.
3. Name it `examforge-api` and click **Deploy**.
4. Click **Edit Code** (Quick Edit).
5. Delete the default code, copy the entire content of [`cloudflare-backend/worker.js`](./worker.js), paste it in, and click **Save and Deploy**.
6. Cloudflare will give you a public HTTPS URL like:
   `https://examforge-api.yoursubdomain.workers.dev`
7. In the left menu, click **Storage & Databases** -> **D1 SQL Database** -> **Create Database**. Name it `examforge-db`.
8. In your Worker's **Settings** -> **Bindings**, add a D1 Database binding named `DB` linked to `examforge-db`.
9. Go to your D1 database -> **Console**, paste the contents of [`cloudflare-backend/schema.sql`](./schema.sql), and click **Execute**.

Done! Your backend and database are now live in the cloud 100% free!

---

## Method 2: Deploy in 30 Seconds via Terminal (Wrangler)

```bash
cd cloudflare-backend
npx wrangler login
npx wrangler d1 create examforge-db
# Copy the database_id printed by wrangler and put it in wrangler.toml
npx wrangler d1 execute examforge-db --file=./schema.sql
npx wrangler deploy
```

---

## Connecting the Frontend (`index.html`)

Once your Worker is deployed, you can either:
1. Set the URL in `index.html` at the top:
   ```html
   <script>window.EXAMFORGE_API_URL = "https://examforge-api.yoursubdomain.workers.dev";</script>
   ```
2. Or in the Owner console on your site, paste your Worker URL into the Backend Configuration field!

All devices, phones, and schools will now authenticate directly against your Cloudflare D1 cloud database with 100% uptime and 0 server fees!
