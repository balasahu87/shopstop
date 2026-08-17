from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional
from uuid import uuid4
from datetime import datetime, timezone
from .agents import CommerceOrchestrator

app=FastAPI(title='ShopStop Multi-Agent Commerce API',version='2.0.0',description='Full commerce and multi-agent orchestration API')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

PRODUCTS=[
 {'id':'p1','name':'Aurora Wireless Headphones','category':'Audio','price':129.99,'rating':4.8,'emoji':'🎧','color':'violet','description':'Adaptive ANC, spatial audio and 40-hour battery.'},
 {'id':'p2','name':'Orbit Smart Watch','category':'Wearables','price':189.00,'rating':4.7,'emoji':'⌚','color':'blue','description':'Health insights, GPS and all-day battery.'},
 {'id':'p3','name':'Nimbus Laptop Stand','category':'Workspace','price':79.50,'rating':4.9,'emoji':'💻','color':'cyan','description':'Aluminium ergonomic stand for modern desks.'},
 {'id':'p4','name':'Pulse Mechanical Keyboard','category':'Workspace','price':149.00,'rating':4.6,'emoji':'⌨️','color':'pink','description':'Hot-swappable switches and wireless connectivity.'},
 {'id':'p5','name':'Nova Smart Speaker','category':'Smart Home','price':99.00,'rating':4.5,'emoji':'🔊','color':'orange','description':'Room-filling sound with voice automation.'},
 {'id':'p6','name':'Halo 4K Webcam','category':'Cameras','price':119.00,'rating':4.8,'emoji':'📷','color':'green','description':'4K HDR camera with auto framing and dual mics.'},
]
CARTS:Dict[str,List[dict]]={}; ORDERS:List[dict]=[]; orchestrator=CommerceOrchestrator()
class CartItem(BaseModel): product_id:str; quantity:int=Field(default=1,ge=1,le=20)
class Checkout(BaseModel): cart_id:str; email:EmailStr='demo@shopstop.dev'; address:str=Field(default='Demo address',min_length=5)
class AgentRequest(BaseModel): message:str=Field(min_length=2,max_length=2000); cart_id:str='demo'
class OrderStatus(BaseModel): status:str

def find_product(pid): return next((p for p in PRODUCTS if p['id']==pid),None)
def get_raw_cart(cid): return CARTS.setdefault(cid,[])
def cart_view(cid):
 items=[]
 for x in get_raw_cart(cid):
  p=find_product(x['product_id'])
  if p: items.append({**p,'quantity':x['quantity'],'line_total':round(p['price']*x['quantity'],2),'product_id':p['id']})
 subtotal=round(sum(i['line_total'] for i in items),2); shipping=0 if subtotal>=100 else (9.99 if items else 0); tax=round(subtotal*.08,2)
 return {'cart_id':cid,'items':items,'subtotal':subtotal,'shipping':shipping,'tax':tax,'total':round(subtotal+shipping+tax,2)}

@app.get('/api/health')
def health(): return {'status':'ok','service':'shopstop-api','version':app.version,'timestamp':datetime.now(timezone.utc).isoformat()}

@app.get('/api/categories')
def categories(): return sorted({p['category'] for p in PRODUCTS})
@app.get('/api/products')
def products(q:str='',category:Optional[str]=None,min_price:Optional[float]=Query(None,ge=0),max_price:Optional[float]=Query(None,ge=0),sort:str='featured'):
 data=[p for p in PRODUCTS if (not q or q.lower() in (p['name']+' '+p['category']+' '+p['description']).lower()) and (not category or p['category'].lower()==category.lower()) and (min_price is None or p['price']>=min_price) and (max_price is None or p['price']<=max_price)]
 if sort=='price_asc': data.sort(key=lambda x:x['price'])
 elif sort=='price_desc': data.sort(key=lambda x:x['price'],reverse=True)
 elif sort=='rating': data.sort(key=lambda x:x['rating'],reverse=True)
 return data
@app.get('/api/products/{product_id}')
def product(product_id:str):
 p=find_product(product_id)
 if not p: raise HTTPException(404,'Product not found')
 return p

@app.get('/api/cart/{cart_id}')
def get_cart(cart_id:str): return cart_view(cart_id)
@app.post('/api/cart/{cart_id}/items')
def add_item(cart_id:str,item:CartItem):
 if not find_product(item.product_id): raise HTTPException(404,'Product not found')
 c=get_raw_cart(cart_id); x=next((z for z in c if z['product_id']==item.product_id),None)
 if x:x['quantity']=min(20,x['quantity']+item.quantity)
 else:c.append(item.model_dump())
 return cart_view(cart_id)
@app.patch('/api/cart/{cart_id}/items/{product_id}')
def update_item(cart_id:str,product_id:str,quantity:int=Query(1,ge=0,le=20)):
 c=get_raw_cart(cart_id); x=next((z for z in c if z['product_id']==product_id),None)
 if not x: raise HTTPException(404,'Cart item not found')
 if quantity==0:c.remove(x)
 else:x['quantity']=quantity
 return cart_view(cart_id)
@app.delete('/api/cart/{cart_id}/items/{product_id}')
def remove_item(cart_id:str,product_id:str):
 CARTS[cart_id]=[x for x in get_raw_cart(cart_id) if x['product_id']!=product_id]; return cart_view(cart_id)
@app.delete('/api/cart/{cart_id}')
def clear_cart(cart_id:str): CARTS[cart_id]=[]; return cart_view(cart_id)

@app.post('/api/checkout')
def checkout(payload:Checkout):
 summary=cart_view(payload.cart_id)
 if not summary['items']: raise HTTPException(400,'Cart is empty')
 order={'id':'ORD-'+uuid4().hex[:8].upper(),'status':'confirmed','created_at':datetime.now(timezone.utc).isoformat(),**summary,'email':str(payload.email),'address':payload.address}
 ORDERS.append(order); CARTS[payload.cart_id]=[]; return order
@app.get('/api/orders')
def orders(email:Optional[str]=None): return [o for o in ORDERS if not email or o['email']==email]
@app.get('/api/orders/{order_id}')
def order(order_id:str):
 o=next((x for x in ORDERS if x['id']==order_id),None)
 if not o: raise HTTPException(404,'Order not found')
 return o
@app.post('/api/orders/{order_id}/cancel')
def cancel_order(order_id:str):
 o=next((x for x in ORDERS if x['id']==order_id),None)
 if not o: raise HTTPException(404,'Order not found')
 if o['status'] not in ('confirmed','processing'): raise HTTPException(409,'Order cannot be cancelled')
 o['status']='cancelled'; return o

@app.post('/api/agents/run')
def run_agents(req:AgentRequest): return orchestrator.run(req.message,cart_view(req.cart_id),PRODUCTS)
@app.get('/api/agents')
def list_agents(): return [{'name':a.name,'capabilities':a.__class__.__name__} for a in orchestrator.agents]
@app.get('/api/agents/{agent_name}')
def agent_detail(agent_name:str):
 a=next((x for x in orchestrator.agents if x.name.lower().replace(' ','-')==agent_name.lower()),None)
 if not a: raise HTTPException(404,'Agent not found')
 return {'name':a.name,'implementation':a.__class__.__name__,'status':'ready'}

@app.get('/api/analytics/overview')
def analytics():
 revenue=round(sum(o['total'] for o in ORDERS if o['status']!='cancelled'),2)
 return {'orders':len(ORDERS),'revenue':revenue,'active_carts':len(CARTS),'products':len(PRODUCTS),'agents':len(orchestrator.agents)}
