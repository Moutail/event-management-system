#!/usr/bin/env python
"""
Smoke test API: JWT auth, create virtual event, fetch it.
"""
import requests
from datetime import datetime, timedelta

BASE = 'http://localhost:8001/api'

def run():
    print('🔌 Testing API on', BASE)
    # 1) Obtain token (use demo credentials if exist)
    # If you don't have a user yet, create via admin or register endpoint first.
    try:
        r = requests.post(f"{BASE}/auth/token/", json={"username": "admin", "password": "admin"})
        if r.status_code != 200:
            print('⚠️  Cannot obtain token with admin/admin. Please login and set tokens in frontend.')
            return
        token = r.json()['access']
        headers = { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json' }
        print('✅ Token obtained')
    except Exception as e:
        print('❌ Error obtaining token:', e)
        return

    # 2) Create virtual event (draft)
    payload = {
        "event_data": {
            "title": "Smoke Test Virtual Event",
            "description": "Created by smoke test",
            "event_type": "virtual",
            "start_date": (datetime.utcnow() + timedelta(days=2)).isoformat() + 'Z',
            "end_date": (datetime.utcnow() + timedelta(days=2, hours=2)).isoformat() + 'Z',
            "location": "Zoom",
            "price": "0.00",
            "is_free": True,
            "status": "draft"
        },
        "platform": "zoom",
        "meeting_id": "SMOKE123",
        "meeting_password": "123456",
        "auto_record": True,
        "allow_chat": True,
        "allow_screen_sharing": True,
        "waiting_room": True,
        "access_instructions": "Join on time.",
        "technical_requirements": "Any browser"
    }
    r = requests.post(f"{BASE}/virtual-events/", json=payload, headers=headers)
    print('POST /virtual-events ->', r.status_code)
    if r.status_code not in (200, 201):
        print(r.text[:500])
        return
    event = r.json()
    ve_id = event.get('id') or event.get('event', {}).get('id')
    print('✅ Virtual event created, id =', ve_id)

    # 3) Fetch list
    r = requests.get(f"{BASE}/virtual-events/", headers=headers)
    print('GET /virtual-events ->', r.status_code)
    if r.ok:
        data = r.json()
        print('Count:', len(data.get('results', data)))

if __name__ == '__main__':
    run()
