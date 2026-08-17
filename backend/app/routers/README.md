# API domains

The backend exposes domain APIs for:

- Catalog: products, search, category, filters and sorting
- Cart: read, add, update, remove and clear
- Checkout: order creation
- Orders: list, detail and cancellation
- AI: agent registry, agent status and orchestrated workflows
- Analytics: portfolio/demo operational overview
- Health: service readiness

The orchestration layer is implemented under `app/agents/` with explicit agent contracts and a coordinator. The current runtime is deterministic and has no external model dependency, making the demo reproducible.
