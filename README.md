# Aura: The Secure Agentic GitHub Orchestrator

**Aura** is a powerful AI-driven agent designed to manage and orchestrate GitHub repositories securely. Built for the **Auth0 "Authorized to Act" Hackathon**, Aura pushes the boundaries of autonomous agents by integrating **Auth0 for AI Agents** (Token Vault) to ensure every high-stakes action is authorized by a human through step-up authentication.

![Aura Dashboard Shot](https://raw.githubusercontent.com/aura-ai/aura/main/assets/banner.png)

---

## 🚀 Key Features

- **Autonomous Planning**: Input complex prompts like *"Archive my unused repositories from 2023"* and Aura will generate a multi-step execution plan.
- **Auth0 Token Vault Integration**: Aura never sees your raw GitHub credentials. It requests scoped, short-lived tokens from Auth0 on-the-fly.
- **Dynamic Policy Enforcement**: Every action is evaluated for "risk" (Low, Medium, High). High-risk actions like repository deletion trigger a mandatory human approval flow (MFA/Step-up Auth).
- **Immutable Audit Logging**: Every stage—from LLM planning to final execution—is logged to a secure, local database for full transparency and accountability.
- **Beautiful Dashboard**: A modern, glassmorphic UI built with Next.js and Tailwind CSS.

---

## 🏗 Architecture

Aura follows a modern, decoupled architecture:

- **Frontend**: Next.js 14, Tailwind CSS, Auth0 Next.js SDK.
- **Backend**: FastAPI (Python), SQLAlchemy (SQLite), OpenAI GPT-4o-mini.
- **Identity Layer**: Auth0 for AI Agents (Token Vault) manages the OAuth lifecycle and user consent.
- **Execution Layer**: GitHub REST API.

---

## 🛠 Setup & Installation

### Prerequisites

- Node.js 18+
- Python 3.10+
- An Auth0 Tenant with **Auth0 for AI Agents** enabled.
- A GitHub Personal Access Token (configured in the Auth0 Dashboard).

### 1. Backend Setup

```bash
cd aura-backend
python -m venv .venv
source .venv/bin/activate  # Or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Update .env with your credentials
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd aura-frontend
npm install
cp .env.local.example .env.local
# Update .env.local with your credentials
npm run dev
```

---

## 🔒 Security Model: "Authorized to Act"

Aura implements the **Authorized to Act** pattern to solve the "Sovereign AI" trust problem:

1. **Least Privilege**: Aura only requests the specific GitHub scopes (e.g., `read:repos` or `delete_repo`) required for the current task.
2. **Step-up Authentication**: For any destructive or sensitive action, the Auth0 Token Vault returns an `approval_required` status. Aura then directs the user to a secure Auth0 page to provide explicit consent.
3. **No Credential Exposure**: The backend receives a temporary `access_token` from Auth0, which is never stored in the database.

---

## 📄 License

MIT License. See `LICENSE` for details.
