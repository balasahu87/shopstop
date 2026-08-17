from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentContext:
    message: str
    cart: dict
    products: list[dict]
    trace_id: str
    data: dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResult:
    agent: str
    status: str = 'completed'
    result: str = ''
    data: dict[str, Any] = field(default_factory=dict)

class BaseAgent(ABC):
    name = 'Base Agent'
    @abstractmethod
    def run(self, ctx: AgentContext) -> AgentResult: ...
