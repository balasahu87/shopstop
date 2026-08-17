# ShopStop AI 🛍️

A premium **React + FastAPI shopping cart** demonstrating an automated multi-agent commerce workflow and a multi-page customer experience.

## Frontend pages

- **Home** — premium storefront hero, featured products and AI commerce introduction
- **Shop** — searchable product collection with category filters
- **Cart** — item quantity controls, pricing summary and checkout entry point
- **Checkout** — delivery form, order summary and simulated secure payment flow
- **Order Success** — confirmation experience with generated order ID
- **AI Concierge** — five-agent orchestration dashboard with trace ID and recommendations
- **Architecture** — engineering case-study page explaining the production evolution path

The React application is split into reusable components in `frontend/src/App.jsx`, with `main.jsx` as the entry point. The UI includes reusable navigation, product cards, cart panel, checkout, AI orchestration, success and architecture components.

## Multi-agent workflow

```text
Customer → Intent Agent → Catalog Agent → Pricing Agent
                         ↓
              Recommendation Agent → Order Agent
```

The demo uses deterministic local Python agents so it runs without API keys. Each specialist can later be replaced by an LLM/tool adapter while preserving the orchestration contract. The FastAPI API exposes `/api/agents/run` and returns agent events, recommendations and a trace ID.

## Project structure

```text
shopstop/
├── backend/
│   ├── app/main.py
│   ├── app/__init__.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/App.jsx
│   ├── src/main.jsx
│   ├── src/styles.css
│   ├── index.html
│   ├── package.json
│   └── Dockerfile
├── screenshots/
│   ├── storefront.svg
│   ├── ai-orchestration.svg
│   ├── products-page.svg
│   ├── cart-page.svg
│   ├── checkout-page.svg
│   ├── ai-concierge-page.svg
│   └── architecture-page.svg
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
- `POST /api/cart/{cart_id}/items`
- `PATCH /api/cart/{cart_id}/items/{product_id}?quantity=2`
- `DELETE /api/cart/{cart_id}/items/{product_id}`
- `POST /api/checkout`
- `POST /api/agents/run`

## Screenshots / frontend showcase

The `screenshots/` directory contains portfolio-friendly visual captures of the frontend experiences. The existing storefront and AI orchestration captures are retained, and the new captures cover the multi-page UX:

1. `products-page.svg` — product collection and search
2. `cart-page.svg` — shopping bag and pricing summary
3. `checkout-page.svg` — secure checkout
4. `ai-concierge-page.svg` — five-agent workflow dashboard
5. `architecture-page.svg` — engineering architecture case study

The SVG captures are intentionally committed at the repository root under `screenshots/` so reviewers can open them directly from GitHub.

## Architecture decisions

The frontend is dependency-light and componentized. FastAPI provides typed request validation and REST/OpenAPI documentation. Cart/order state is kept in process memory for zero-configuration execution; this is a demo strategy, not a production persistence design.

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

## Portfolio value

This project demonstrates product UX, reusable React component architecture, REST API design, multi-agent orchestration, scalable architecture thinking, hands-on React/Python engineering, checkout workflows, responsive UI and a practical path from demo architecture to distributed production architecture.

## Portfolio

GitHub: https://github.com/balasahu87
