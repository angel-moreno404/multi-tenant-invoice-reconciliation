
# Senior Python Backend Developer – Coding Challenge  
## Multi-Tenant Invoice Reconciliation API

This project implements a **multi-tenant invoice reconciliation system** designed to showcase senior-level backend engineering practices: clean architecture, transaction safety, idempotency, multi-tenant isolation, and pragmatic AI integration.

The system exposes both **REST (FastAPI)** and **GraphQL (Strawberry)** APIs and supports deterministic reconciliation logic enhanced with an optional AI-powered explanation layer.

---

## ✨ Features

- Multi-tenant architecture with strict data isolation  
- Invoice and bank transaction management  
- Deterministic reconciliation engine with scoring heuristics  
- Match confirmation workflow  
- AI-powered reconciliation explanations with graceful fallback  
- Idempotent bulk import of bank transactions  
- REST + GraphQL APIs backed by a shared service layer  
- Fully tested with `pytest`  

---

## 🏗️ Tech Stack

- **Python** 3.13  
- **FastAPI** – REST API  
- **Strawberry GraphQL** – GraphQL API  
- **SQLAlchemy 2.0** – ORM & persistence  
- **SQLite** – local development DB  
- **pytest** – testing  
- **Optional AI Provider** – OpenAI / Anthropic / mock client  

---

## 🚀 Setup

### 1. Clone & create environment
```bash
git clone <repo-url>
cd invoice-reconciliation
python3.13 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Create a `.env` file:

```env
DATABASE_URL=sqlite:///./app.db
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

---

## ▶️ Running the App

```bash
uvicorn app.main:app --reload
```

- REST API: http://localhost:8000  
- Swagger UI: http://localhost:8000/docs  
- GraphQL Playground: http://localhost:8000/graphql  

---

## 🧱 Architecture Overview

```
app/
 ├── api/
 ├── services/
 ├── models/
 ├── repositories/
 ├── schemas/
 ├── core/
 └── tests/
```

---

## 🧑‍🤝‍🧑 Multi-Tenancy Model

All domain tables are scoped by `tenant_id`.  
All reads and writes are filtered by tenant context.

---

## 🔁 Idempotent Bank Transaction Import

Endpoint:  
`POST /tenants/{tenant_id}/bank-transactions/import`

- Same key + same payload → returns cached response  
- Same key + different payload → **409 Conflict**  

---

## 🔍 Reconciliation Engine

### Heuristics

| Rule | Weight |
|------|--------|
| Exact amount match | +50 |
| Amount within tolerance | +30 |
| Date proximity (±3 days) | +15 |
| Text similarity | +10 |
| Vendor hint | +10 |

---

## 🤖 AI Explanation Layer

- Sends only tenant-authorized data  
- Fully mockable in tests  
- Graceful fallback if AI unavailable  

---

## 🌐 API Overview

### REST
- `POST /tenants`
- `POST /tenants/{tenant_id}/invoices`
- `GET /tenants/{tenant_id}/invoices`
- `DELETE /tenants/{tenant_id}/invoices/{id}`
- `POST /tenants/{tenant_id}/bank-transactions/import`
- `POST /tenants/{tenant_id}/reconcile`
- `POST /tenants/{tenant_id}/matches/{match_id}/confirm`
- `GET /tenants/{tenant_id}/reconcile/explain`

### GraphQL
Queries:
- `tenants`
- `invoices`
- `bankTransactions`
- `explainReconciliation`

Mutations:
- `createTenant`
- `createInvoice`
- `deleteInvoice`
- `importBankTransactions`
- `reconcile`
- `confirmMatch`

---

## 🧪 Testing

```bash
pytest
```

Includes tests for:
- Invoice CRUD  
- Filtering  
- Idempotent imports  
- Reconciliation ranking  
- Match confirmation  
- AI explanation (mock + fallback)  

---

## ⚖️ Key Design Tradeoffs

- Deterministic reconciliation first, AI second  
- Service layer shared by REST and GraphQL  
- SQLite for simplicity and portability  

---

## 🙌 Thank You

Thanks for reviewing this challenge.  
We look forward to your feedback!
