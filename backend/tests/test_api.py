from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health():
    r=client.get('/api/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_products():
    r=client.get('/api/products?q=headphones'); assert r.status_code==200; assert r.json()[0]['id']=='p1'

def test_cart_add_and_remove():
    cid='test'
    r=client.post(f'/api/cart/{cid}/items',json={'product_id':'p1','quantity':2}); assert r.status_code==200
    assert r.json()['items'][0]['quantity']==2
    r=client.delete(f'/api/cart/{cid}/items/p1'); assert r.status_code==200; assert not r.json()['items']

def test_agent_trace():
    r=client.post('/api/agents/run',json={'message':'recommend products','cart_id':'agent-test'}); assert r.status_code==200
    assert len(r.json()['events'])==5
