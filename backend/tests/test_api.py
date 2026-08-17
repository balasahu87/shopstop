from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health():
    r=client.get('/api/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_products_and_filters():
    r=client.get('/api/products?q=headphones'); assert r.status_code==200; assert r.json()[0]['id']=='p1'
    assert client.get('/api/categories').status_code==200
    assert client.get('/api/products?sort=price_asc').status_code==200

def test_cart_add_update_remove_clear():
    cid='test'
    r=client.post(f'/api/cart/{cid}/items',json={'product_id':'p1','quantity':2}); assert r.status_code==200
    assert r.json()['items'][0]['quantity']==2
    r=client.patch(f'/api/cart/{cid}/items/p1?quantity=1'); assert r.status_code==200
    r=client.delete(f'/api/cart/{cid}/items/p1'); assert r.status_code==200; assert not r.json()['items']
    assert client.delete(f'/api/cart/{cid}').status_code==200

def test_agent_registry_and_trace():
    assert len(client.get('/api/agents').json())==5
    r=client.post('/api/agents/run',json={'message':'recommend products','cart_id':'agent-test'}); assert r.status_code==200
    assert len(r.json()['events'])==5

def test_checkout_and_order():
    cid='checkout-test'
    client.post(f'/api/cart/{cid}/items',json={'product_id':'p1','quantity':1})
    r=client.post('/api/checkout',json={'cart_id':cid,'email':'test@example.com','address':'123 Demo Street'})
    assert r.status_code==200
    oid=r.json()['id']
    assert client.get(f'/api/orders/{oid}').status_code==200
    assert client.post(f'/api/orders/{oid}/cancel').status_code==200
