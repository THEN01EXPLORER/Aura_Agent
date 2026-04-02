# Hackathon Submission Materials: Aura

---

## 📝 Part 1: Project Description (Features & Functionality)

**Aura: The Secure Agentic GitHub Orchestrator**

**The Problem:**
As AI agents become more autonomous, the risk of "prompt injection" or "erroneous execution" leading to catastrophic data loss (e.g., deleting critical repositories) increases. Most current agents either run with broad, over-privileged tokens or require constant, manual copy-pasting of API keys.

**The Solution:**
Aura solves this by implementing the **Authorized to Act** pattern using **Auth0 for AI Agents** (Token Vault). Aura is an intelligent GitHub manager that understands natural language intent but remains strictly bound by human-defined security policies.

**Key Features:**
1.  **Intent-Driven Planning**: Aura uses an LLM (GPT-4o-mini) to translate user prompts (e.g., *"Clean up my personal projects from last year"*) into structured multi-step plans.
2.  **Auth0 Token Vault Integration**: Aura never stores or sees a user's GitHub Personal Access Token. Instead, it requests scoped, short-lived tokens on-the-fly.
3.  **Real-time Policy Evaluation**: Every planned action is evaluated for "risk" (Low, Medium, High). 
    - **Read-only actions** (listing repos) use a low-risk scope and are executed immediately.
    - **Safe actions** (creating a repo) are executed with a "public_repo" scope.
    - **High-stakes actions** (deleting or archiving) trigger a mandatory `approval_required` status from Auth0, forcing a human-in-the-loop step-up authentication.
4.  **Immutable Audit Logs**: Every decision—from the initial LLM plan to the final API result—is recorded in a secure database, providing a complete audit trail for compliance and safety.
5.  **Modern Dashboard**: A fast, responsive UI built with Next.js and Tailwind CSS that visualizes the "thinking" process of the agent.

---

## 🚀 Part 2: Bonus Blog Post (250+ Words)

**Aura: Bridging the Sovereign Trust Gap with Auth0 Token Vault**

The rise of "Sovereign AI"—agents that run locally on our machines or browsers—presents a unique security paradox. We want agents that can act on our behalf across our digital lives (GitHub, Slack, Google Calendar), but we rightfully fear giving them "the keys to the castle." 

During the **Authorized to Act Hackathon**, we built **Aura**, a GitHub orchestrator that demonstrates how to solve this "Trust Gap" using the **Auth0 Token Vault**.

### The Architecture of Trust

The core achievement of Aura is its strict separation of *Intent* from *Authority*. In a traditional agent flow, the agent is given a long-lived API key and total control. In Aura, the agent is a "requestor" rather than an "owner." 

When a user asks Aura to "Archive my old projects," the agent doesn't just call the GitHub API. It first sends its structured plan to a backend policy engine. This engine identifies that `archive_repo` is a high-risk operation and requests a specific `write:repos` scope from the Auth0 Token Vault. 

### Why Token Vault is a Game Changer for Developers

Using the **Auth0 for AI Agents** Token Vault allowed us to focus on the *intelligence* of the agent rather than the *plumbing* of OAuth. 
- **OAuth Complexity**: Gone. We didn't have to build complex "Connect to GitHub" flows or manage token refreshes. 
- **Zero-Trust for Agents**: The agent itself never touches the raw credentials. It only receives a scoped access token *after* the user has provided explicit consent via step-up authentication.
- **Dynamic Scoping**: We could request different levels of access (read vs. delete) based on the specific task the agent was trying to perform, perfectly adhering to the principle of least privilege.

### The Future of AI Agents

Aura isn't just a GitHub tool; it’s a blueprint for the future of "Authorized to Act." By using Auth0 as the identity and authorization layer for AI, we can finally build agents that are as powerful as they are safe. Users stay in control, agents stay autonomous, and the boundary between the two is secured by the industry standard in identity management.

Building with Token Vault wasn't just about passing a hackathon requirement—it was about discovering the missing piece of the agentic puzzle: **verifiable human consent**.

---

## 🔗 Submission Links

- **Repository**: [Your Public GitHub Repository URL]
- **Published App**: [Your Vercel/Deployed App URL]
- **Demo Video**: [Your YouTube/Vimeo Demo Link]
