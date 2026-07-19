# 📚 RBAC System Documentation Index

Welcome to the complete documentation index for the Role-Based Access Control (RBAC) implementation of the FastAPI AuthBase API.

## 🚀 Getting Started

**New to the system? Start here:**
1. **[../README.md](../README.md)** - Project overview, features, and quick setup overview.
2. **[QUICK_START.md](QUICK_START.md)** - Step-by-step setup, configuration, Alembic migration, seeding, and full API endpoint reference.

---

## 📖 Available Documents

| Document | Purpose | Audience |
| :--- | :--- | :--- |
| **[QUICK_START.md](QUICK_START.md)** | Step-by-step installation, Alembic migration, seeding, and default credentials reference. | Human / Agentic AI |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System overview, database entity relationship schemas, request flow, and code integration guidelines. | Human / Agentic AI |
| **[PRD.md](PRD.md)** | Product requirements, user stories, database constraints, business rules, and non-goals. | Product Team / QA |

---

## 🎯 Key Concepts Reference

* **Role:** Group of users sharing access limits (e.g., `admin`, `user`).
* **Menu:** Application feature tree or module (e.g., `Dashboard`, `Users`). Supports parent-child relationships.
* **Action:** Atomic operations allowable inside modules (e.g., `create`, `read`, `update`, `delete`).
* **Permission Mapping:** 3D intersection mapping a **Role** to a specific **Action** on a **Menu**.
* **Audit Trail:** Append-only transaction log monitoring sensitive and state-changing events.
