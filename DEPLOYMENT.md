# Aura Deployment Guide

To deploy Aura for the hackathon, you will need to host the backend (FastAPI) and the frontend (Next.js) separately.

---

## 1. Backend Deployment: [Render](https://render.com/)

Render is ideal for the FastAPI backend.

### **Step-by-Step Configuration**
1.  **Create New Service**: Click the **"+ New"** button in your Render dashboard and select [**Web Service**](https://dashboard.render.com/select-repo?type=web).
2.  **Connect Repository**: Connect your GitHub account and select the `Aura_Agent` repository.
3.  **Project Settings**:
    *   **Name**: `aura-backend` (or similar)
    *   **Root Directory**: `aura-backend`
    *   **Environment**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables**: Click **"Advanced"** and add all variables from your local `aura-backend/.env`.
    *   **CRITICAL**: Set `DEBUG=false` for production.
    *   **CRITICAL**: Update `CORS_ORIGINS` to include your future Vercel URL (e.g. `["https://your-app.vercel.app"]`).

---

## 2. Frontend Deployment: [Vercel](https://vercel.com/)

Vercel is the best platform for Next.js applications.

### **Step-by-Step Configuration**
1.  **Import Project**: Log in to Vercel and import your `Aura_Agent` repository.
2.  **Project Settings**:
    *   **Framework Preset**: Next.js
    *   **Root Directory**: `aura-frontend`
3.  **Environment Variables**: Add the following from your `aura-frontend/.env.local`:
    *   `AUTH0_SECRET`
    *   `AUTH0_BASE_URL` (Your Vercel URL, once deployed)
    *   `AUTH0_ISSUER_BASE_URL`
    *   `AUTH0_CLIENT_ID`
    *   `AUTH0_CLIENT_SECRET`
    *   `NEXT_PUBLIC_API_URL`: **Set this to your Render Backend URL** (e.g. `https://aura-backend.onrender.com`).

---

## 3. Auth0 Dashboard Updates

Once your sites are live, you must update the **Auth0 Dashboard** so it trusts your new production URLs:

1.  **Applications → Aura Frontend**:
    *   **Allowed Callback URLs**: Add `https://your-vercel-app.vercel.app/api/auth/callback`
    *   **Allowed Logout URLs**: Add `https://your-vercel-app.vercel.app/`
    *   **Allowed Web Origins**: Add `https://your-vercel-app.vercel.app/`
2.  **API → Aura API**:
    *   Ensure the **Identifier** matches the `AUTH0_AUDIENCE` you set in your env vars.

---

## 4. Final Verification
1.  Visit your Vercel URL.
2.  Log in using GitHub.
3.  Type a prompt and verify the backend planning/execution works.
4.  Copy these live URLs into your **SUBMISSION.md**! 🚀
