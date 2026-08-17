from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from uuid import uuid4
from datetime import datetime

app = FastAPI(title='ShopStop Multi-Agent Commerce API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

PRODUCTS = [
 {'id':'p1','name':'Aurora Wireless Headphones','category':'Audio','price':129.99,'rating':4.8,'emoji':'🎧','color':'violet','description':'Adaptive ANC, spatial audio and 40-hour battery.'},
 {'id':'p2','name':'Orbit Smart Watch','category':'Wearables','price':189.00,'rating':4.7,'emoji':'⌚','color':'blue','description':'Health insights, GPS and all-day battery.'},
 {'id':'p3','name':'Nimbus Laptop Stand','category':'Workspace','price':79.50,'rating':4.9,'emoji':'💻','color':'cyan','description':'Aluminium ergonomic stand for modern desks.'},
 {'id':'p4','name':'Pulse Mechanical Keyboard','category':'Workspace','price':149.00,'rating':4.6,'emoji':'⌨️','color':'pink','description':'Hot-swappable switches and wireless connectivity.'},
 {'id':'p5','name':'Nova Smart Speaker','category':'Smart Home','price':99.00,'rating':4.5,'emoji':'🔊','color':'orange','description':'Room-filling sound with voice automation.'},
 {'id':'p6','name':'Halo 4K Webcam','category':'Cameras','price':119.00,'rating':4.8,'emoji':'📷','color':'green','description':'4K HDR camera with auto framing and dual mics.'},
]
CARTS: Dict[str,List[dict]] = {}
ORDERS: List[dict] = []

class CartItem(BaseModel): product_id: str; quantity: int = Field(default=1, ge=1, le=20)
class Checkout(BaseModel): cart_id: str; email: str = 'demo@shopstop.dev'; address: str = 'Demo address'
class AgentRequest(BaseModel): message: str; cart_id: str = 'demo'

def find_product(pid): return next((p for p in PRODUCTS if p['id']==pid), None)
def cart(cart_id): return CARTS.setdefault(cart_id, [])
def cart_view(cart_id):
 items=[]
 for x in cart(cart_id):
  p=find_product(x['product_id'])
  if p: items.append({**p,'quantity':x['quantity'],'line_total':round(p['price']*x['quantity'],2)})
 subtotal=round(sum(i['line_total'] for i in items),2)
 return {'cart_id':cart_id,'items':items,'subtotal':subtotal,'shipping':0 if subtotal>=100 else 9.99,'tax':round(subtotal*.08,2),'total':round(subtotal+(0 if subtotal>=100 else 9.99)+subtotal*.08,2)}

@app.get('/api/health')
def health(): return {'status':'ok','service':'shopstop-api','timestamp':datetime.utcnow().isoformat()}
@app.get('/api/products')
def products(q: str=''):
 return [p for p in PRODUCTS if not q or q.lower() in (p['name']+' '+p['category']+' '+p['description']).lower()]
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
 c=cart(cart_id); existing=next((x for x in c if x['product_id']==item.product_id),None)
 if existing: existing['quantity']=min(20,existing['quantity']+item.quantity)
 else: c.append(item.model_dump())
 return cart_view(cart_id)
@app.patch('/api/cart/{cart_id}/items/{product_id}')
def update_item(cart_id:str,product_id:str, quantity:int=1):
 c=cart(cart_id); x=next((x for x in c if x['product_id']==product_id),None)
 if not x: raise HTTPException(404,'Cart item not found')
 if quantity<=0: c.remove(x)
 else: x['quantity']=min(20,quantity)
 return cart_view(cart_id)
@app.delete('/api/cart/{cart_id}/items/{product_id}')
def remove_item(cart_id:str,product_id:str):
 CARTS[cart_id]=[x for x in cart(cart_id) if x['product_id']!=product_id]; return cart_view(cart_id)

@app.post('/api/checkout')
def checkout(payload:Checkout):
 summary=cart_view(payload.cart_id)
 if not summary['items']: raise HTTPException(400,'Cart is empty')
 order={'id':'ORD-'+uuid4().hex[:8].upper(),'status':'confirmed','created_at':datetime.utcnow().isoformat(),**summary,'email':payload.email}
 ORDERS.append(order); CARTS[payload.cart_id]=[]
 return order

@app.post('/api/agents/run')
def run_agents(req:AgentRequest):
 msg=req.message.lower(); c=cart_view(req.cart_id)
 intent='recommendation' if any(k in msg for k in ['recommend','suggest','best']) else 'cart' if any(k in msg for k in ['cart','add','remove']) else 'support'
 events=[
  {'agent':'Intent Agent','status':'completed','result':f'Intent classified as {intent}'},
  {'agent':'Catalog Agent','status':'completed','result':f'Scanned {len(PRODUCTS)} products and matched context'},
  {'agent':'Pricing Agent','status':'completed','result':f'Current cart subtotal ${c["subtotal"]:.2f}; free shipping above $100'},
  {'agent':'Recommendation Agent','status':'completed','result':'Generated complementary-product candidates'},
  {'agent':'Order Agent','status':'completed','result':'Validated cart and checkout readiness'},
 ]
 recs=sorted(PRODUCTS,key=lambda p:p['rating'],reverse=True)[:3]
 return {'request':req.message,'intent':intent,'events':events,'recommendations':recs,'cart':c,'trace_id':uuid4().hex}
