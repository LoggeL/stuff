import json
import pytest
from src.models import Location, Item, Tag

def test_index_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.location.endswith('/items')

def test_locations_get(client, sample_data):
    response = client.get('/locations')
    assert response.status_code == 200
    assert b'Test Location 1' in response.data
    assert b'Test Location 2' in response.data

def test_locations_post(client):
    response = client.post('/locations',
                         data=json.dumps({'name': 'New Location'}),
                         content_type='application/json',
                         headers={'Accept': 'application/json'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data
    assert data['name'] == 'New Location'

def test_items_get(client, sample_data):
    response = client.get('/items')
    assert response.status_code == 200
    assert b'Test Item 1' in response.data
    assert b'Test Item 2' in response.data

def test_items_search(client, sample_data):
    # Test search by name
    response = client.get('/items?search=Item 1')
    assert response.status_code == 200
    assert b'Test Item 1' in response.data
    assert b'Test Item 2' not in response.data

    # Test search by tag
    response = client.get('/items?tag=test-tag-1')
    assert response.status_code == 200
    assert b'Test Item 1' in response.data
    assert b'Test Item 2' in response.data

    # Test search by location
    location_id = sample_data['locations'][0].id
    response = client.get(f'/items?location_id={location_id}')
    assert response.status_code == 200
    assert b'Test Item 1' in response.data
    assert b'Test Item 2' not in response.data

def test_items_post(client, sample_data):
    location_id = sample_data['locations'][0].id
    data = {
        'name': 'New Item',
        'quantity': '2',
        'description': 'New Description',
        'location_id': location_id,
        'tags': 'new-tag, test-tag-1'
    }
    response = client.post('/items',
                          data=data,
                          headers={'Accept': 'application/json'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data
    assert data['name'] == 'New Item'

def test_item_detail(client, sample_data):
    item_id = sample_data['items'][0].id
    response = client.get(f'/items/{item_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Test Item 1'
    assert data['quantity'] == 5
    assert data['description'] == 'Test Description 1'
    assert len(data['tags']) == 1
    assert data['tags'][0]['name'] == 'test-tag-1'

def test_item_qr(client, sample_data):
    item_id = sample_data['items'][0].id
    response = client.get(f'/items/{item_id}/qr')
    assert response.status_code == 200
    assert response.mimetype == 'image/png'

def test_tags_get(client, sample_data):
    response = client.get('/tags')
    assert response.status_code == 200
    assert b'test-tag-1' in response.data
    assert b'test-tag-2' in response.data

def test_tags_post(client):
    response = client.post('/tags',
                         data=json.dumps({'name': 'new-tag'}),
                         content_type='application/json',
                         headers={'Accept': 'application/json'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data
    assert data['name'] == 'new-tag'

def test_subitems(client, sample_data):
    parent_id = sample_data['items'][0].id
    child_id = sample_data['items'][1].id
    
    # Add subitem
    response = client.post(f'/items/{parent_id}/subitems',
                         data=json.dumps({'subitem_id': child_id}),
                         content_type='application/json')
    assert response.status_code == 200
    
    # Get subitems
    response = client.get(f'/items/{parent_id}/subitems')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['id'] == child_id 