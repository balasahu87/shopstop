from uuid import uuid4
from .base import AgentContext
from .commerce_agents import IntentAgent,CatalogAgent,PricingAgent,RecommendationAgent,OrderAgent

class CommerceOrchestrator:
    def __init__(self):
        self.agents=[IntentAgent(),CatalogAgent(),PricingAgent(),RecommendationAgent(),OrderAgent()]
    def run(self,message,cart,products):
        trace_id=uuid4().hex
        ctx=AgentContext(message=message,cart=cart,products=products,trace_id=trace_id)
        events=[]
        for agent in self.agents:
            try:
                r=agent.run(ctx)
                events.append({'agent':r.agent,'status':r.status,'result':r.result,'data':r.data})
            except Exception as exc:
                events.append({'agent':agent.name,'status':'failed','result':str(exc),'data':{}})
        return {'request':message,'trace_id':trace_id,'intent':ctx.data.get('intent','support'),'events':events,'recommendations':ctx.data.get('recommendations',[]),'pricing':ctx.data.get('pricing'),'cart':cart}
