# -*- coding: utf-8 -*-
import json
import urllib.request
import time

PRIMARY_URL = "https://api.restful-api.dev/objects/ff808181a09d98f701a1978284d8001f"
BACKUP_URL = "https://api.restful-api.dev/objects/ff808181a09d98f701a1ab786b1d415a"

def fetch_cloud(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def push_cloud(url, schools, owner_pwd=""):
    payload = json.dumps({
        "name": "examforge_schools_global",
        "data": {
            "version": int(time.time() * 1000),
            "schools": schools,
            "owner_master_pwd": owner_pwd
        }
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, method="PUT")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status in (200, 201)

def run_test():
    print("Step 1: Reading existing schools from cloud...")
    primary_data = fetch_cloud(PRIMARY_URL)
    schools = primary_data.get("data", {}).get("schools", [])
    print(f"Current schools count in primary: {len(schools)}")

    # Ensure baseline schools exist
    test_school = {
        "name": "Iqra National School",
        "principal": "Dr. Muhammad Farooq",
        "username": "iqra",
        "password": "123",
        "quota": "Unlimited",
        "phone": "+923215423874",
        "createdAt": "2026-11-05T12:00:00.000Z"
    }

    # Add or update
    schools = [s for s in schools if s.get("username") != "iqra"]
    schools.insert(0, test_school)

    print("Step 2: Owner creates new school 'iqra' and pushes to BOTH Primary & Backup endpoints...")
    ok1 = push_cloud(PRIMARY_URL, schools)
    ok2 = push_cloud(BACKUP_URL, schools)
    print(f"Push to Primary: {'SUCCESS' if ok1 else 'FAILED'}")
    print(f"Push to Backup: {'SUCCESS' if ok2 else 'FAILED'}")
    assert ok1 or ok2, "Both pushes failed!"

    print("\nStep 3: Simulating Other Device (e.g. mobile phone in another city) querying cloud...")
    device_b_schools = None
    for endpoint in [PRIMARY_URL, BACKUP_URL]:
        try:
            data = fetch_cloud(endpoint)
            s_list = data.get("data", {}).get("schools", [])
            if s_list:
                device_b_schools = s_list
                print(f"Device B successfully pulled from {endpoint}")
                break
        except Exception as e:
            print(f"Device B endpoint fallback due to: {e}")

    assert device_b_schools is not None, "Device B could not pull any schools!"

    print(f"Total schools received on Device B: {len(device_b_schools)}")
    matched = next((s for s in device_b_schools if (s.get("username") or "").lower() == "iqra" and s.get("password") == "123"), None)
    
    if matched:
        print(f"SUCCESS: School '{matched['name']}' logged in on Device B with username '{matched['username']}' and password '{matched['password']}'!")
    else:
        raise AssertionError("Device B failed to find and authenticate school 'iqra'!")

    print("\nALL MULTI-DEVICE CLOUD SYNCHRONIZATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_test()
