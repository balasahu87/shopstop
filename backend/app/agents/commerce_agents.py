from .base import BaseAgent, AgentContext, AgentResult

class IntentAgent(BaseAgent):
    name='Intent Agent'
    def run(self,ctx):
        m=ctx.message.lower()
        intent='recommendation' if any(x in m for x in ('recommend','suggest','best','similar')) else 'cart' if any(x in m for x in ('cart','add','remove','quantity')) else 'checkout' if any(x in m for x in ('checkout','order','buy')) else 'support'
        ctx.data['intent']=intent
        return AgentResult(self.name,result=f'Intent classified as {intent}',data={'intent':intent})

class CatalogAgent(BaseAgent):
    name='Catalog Agent'
    def run(self,ctx):
        intent=ctx.data.get('intent','support')
        terms=[x for x in ctx.message.lower().split() if len(x)>2]
        matches=[p for p in ctx.products if any(t in (p['name']+' '+p['category']+' '+p['description']).lower() for t in terms)]
        if not matches: matches=sorted(ctx.products,key=lambda p:p['rating'],reverse=True)
        ctx.data['candidates']=matches[:6]
        return AgentResult(self.name,result=f'Scanned {len(ctx.products)} products and selected {len(matches[:6])} candidates',data={'candidates':matches[:6]})

class PricingAgent(BaseAgent):
    name='Pricing Agent'
    def run(self,ctx):
        subtotal=ctx.cart.get('subtotal',0)
        shipping=ctx.cart.get('shipping',0)
        message=f'Cart ${subtotal:.2f}; '+('free shipping applied' if shipping==0 else f'${shipping:.2f} shipping applies')
        ctx.data['pricing']=message
        return AgentResult(self.name,result=message,data={'subtotal':subtotal,'shipping':shipping,'tax':ctx.cart.get('tax',0),'total':ctx.cart.get('total',0)})

class RecommendationAgent(BaseAgent):
    name='Recommendation Agent'
    def run(self,ctx):
        cart_ids={x.get('product_id') for x in ctx.cart.get('items',[])}
        candidates=ctx.data.get('candidates',ctx.products)
        recs=[p for p in candidates if p['id'] not in cart_ids]
        recs=sorted(recs,key=lambda p:(p['rating'],p['price']),reverse=True)[:3]
        ctx.data['recommendations']=recs
        return AgentResult(self.name,result=f'Generated {len(recs)} complementary recommendations',data={'recommendations':recs})

class OrderAgent(BaseAgent):
    name='Order Agent'
    def run(self,ctx):
        items=ctx.cart.get('items',[])
        readiness='ready' if items else 'empty'
        return AgentResult(self.name,result=f'Checkout readiness: {readiness}',data={'checkout_ready':bool(items)})
