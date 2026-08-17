# ShopStop AI 🛍️

A premium **React + FastAPI shopping cart** demonstrating an automated multi-agent commerce workflow.

## Features

- Premium responsive storefront UI
- Product catalog and search
- Cart add/update/remove flows
- Dynamic subtotal, tax and shipping
- Checkout/order simulation
- Five-agent orchestration trace
- FastAPI REST + automatic OpenAPI/Swagger docs
- Docker Compose full-stack setup
- Mobile-responsive design

## Multi-agent workflow

```text
Customer → Intent Agent → Catalog Agent → Pricing Agent
                         ↓
              Recommendation Agent → Order Agent
```

The demo uses deterministic local Python agents so it runs without API keys. In production, each specialist can be replaced by an LLM/tool adapter while preserving the orchestration contract.

## Structure

```text
shopstop/
├── backend/
│   ├── app/main.py
│   ├── app/__init__.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/main.jsx
│   ├── src/styles.css
│   ├── index.html
│   ├── package.json
│   └── Dockerfile
├── screenshots/
├── docker-compose.yml
└── README.md
```

## Run locally

Requirements: Python 3.11+, Node.js 20+, npm 10+.

```bash
git clone https://github.com/balasahu87/shopstop.git
cd shopstop
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API: http://localhost:8000  
Swagger: http://localhost:8000/docs  
ReDoc: http://localhost:8000/redoc

FastAPI's official tutorial documents the development flow and automatic interactive API docs: https://fastapi.tiangolo.com/tutorial/

### Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

Override the API endpoint if required:

```bash
VITE_API_URL=http://localhost:8000/api npm run dev
```

### Docker

From the repository root:

```bash
docker compose up --build
```

Open http://localhost:5173. Stop with `docker compose down`.

## API

- `GET /api/health`
- `GET /api/products?q=headphones`
- `GET /api/products/{product_id}`
- `GET /api/cart/{cart_id}`
- `POST /api/cart/{cart_id}/items` with `{"product_id":"p1","quantity":1}`
- `PATCH /api/cart/{cart_id}/items/{product_id}?quantity=2`
- `DELETE /api/cart/{cart_id}/items/{product_id}`
- `POST /api/checkout`
- `POST /api/agents/run` with `{"message":"recommend products for my cart","cart_id":"demo"}`

## Architecture decisions

The frontend is intentionally dependency-light. FastAPI provides typed request validation and REST/OpenAPI documentation. FastAPI recommends a multi-file application structure as projects grow: https://fastapi.tiangolo.com/tutorial/bigger-applications/

The demo stores cart/order state in process memory for zero-configuration execution. This is **not** a production persistence strategy.

### Production evolution

- PostgreSQL for catalog/cart/order persistence
- Redis for distributed cart/session caching
- Kafka or another durable bus for domain events
- OAuth/OIDC/JWT for identity
- Payment-provider abstraction with idempotency keys
- OpenTelemetry and centralized metrics/logging
- Background workers for asynchronous agent execution
- API gateway/WAF/rate limiting

### Production agent contract

```text
AgentRequest
   ↓
Orchestrator
   ↓
Agent Registry
   ↓
Tools / Domain Services
   ↓
Aggregator
   ↓
AgentResponse
```

Each agent should have explicit input/output schemas, bounded tool permissions, timeout/retry policy, correlation ID, idempotency, structured telemetry and a human escalation path for high-risk actions. Payment credentials should never be exposed to an LLM agent.

## Testing strategy

Recommended next iteration: Pytest API/contract tests, React component tests, Playwright checkout tests, deterministic agent fixtures, load tests, security tests, and failure-injection tests for agent timeouts/retries.

## Screenshots

The `screenshots/` directory contains repository-friendly SVG visual captures/mockups of the storefront and AI orchestration experience. Replace these with browser-generated PNG captures after running the application if required by a submission process.

## Portfolio value

This project demonstrates product UX, REST API design, multi-agent orchestration, scalable architecture thinking, hands-on React/Python engineering, and a practical path from demo architecture to distributed production architecture.

## License

Portfolio/demo project. Add an explicit open-source license before external redistribution.

---

### Portfolio

GitHub: https://github.com/balasahu87
