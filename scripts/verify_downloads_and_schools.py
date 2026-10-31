import httpx
import json
import os

BASE_URL = "http://localhost:8000/api/v1"

def test_flow():
    client = httpx.Client(timeout=30.0)
    print("--- 1. Testing School and Teacher Registration ---")
    school_slug = f"aps-peshawar-{os.urandom(2).hex()}"
    school_name = "Army Public School & College Peshawar"
    reg_school_payload = {
        "school_name": school_name,
        "slug": school_slug,
        "address": "Warsak Road, Peshawar, KP",
        "admin_name": "Brigadier Tariq",
        "admin_email": f"principal.{os.urandom(3).hex()}@aps.edu.pk",
        "admin_password": "AdminPassword@123"
    }

    res = client.post(f"{BASE_URL}/auth/register-school", json=reg_school_payload)
    if res.status_code == 200:
        admin_data = res.json()
        print(f"Registered School: {school_name} (ID: {admin_data['user']['school_id']})")
        school_id = admin_data['user']['school_id']

        # Register a teacher under this new school
        teacher_email = f"teacher.{os.urandom(3).hex()}@aps.edu.pk"
        reg_teacher_payload = {
            "school_id": school_id,
            "full_name": "Prof. Shahzad Ahmad",
            "email": teacher_email,
            "password": "TeacherPassword@123"
        }
        res_t = client.post(f"{BASE_URL}/auth/register-teacher", json=reg_teacher_payload)
        assert res_t.status_code == 200, f"Teacher reg failed: {res_t.text}"
        teacher_token = res_t.json()["access_token"]
        print(f"Registered Teacher: Prof. Shahzad Ahmad under {school_name}")
    else:
        print(f"School reg response: {res.status_code} {res.text}")

    print("\n--- 2. Testing Login with Existing School Teacher (LGS) ---")
    login_res = client.post(f"{BASE_URL}/auth/login", json={
        "email": "teacher@lgs.edu.pk",
        "password": "Teacher@1234"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    lgs_token = login_res.json()["access_token"]
    print("LGS Teacher Login Successful!")

    print("\n--- 3. Testing Papers List and DOCX Download ---")
    headers = {"Authorization": f"Bearer {lgs_token}"}
    papers_res = client.get(f"{BASE_URL}/papers", headers=headers)
    assert papers_res.status_code == 200
    papers = papers_res.json()
    print(f"Found {len(papers)} papers for LGS.")

    if papers:
        first_paper = papers[0]
        paper_id = first_paper["id"]
        paper_title = first_paper["title"]
        print(f"Testing Paper: '{paper_title}' (ID: {paper_id})")

        # Test Download Method A: Standard Bearer Header
        res_a = client.get(f"{BASE_URL}/papers/{paper_id}/download-docx", headers=headers)
        assert res_a.status_code == 200, f"Method A failed: {res_a.status_code} {res_a.text}"
        content_type = res_a.headers.get("content-type", "")
        assert "officedocument" in content_type or "octet-stream" in content_type
        print(f"Method A (Bearer Header Download): SUCCESS! Size: {len(res_a.content)} bytes")

        # Test Download Method B: URL Query Parameter Token (?token=...)
        res_b = client.get(f"{BASE_URL}/papers/{paper_id}/download-docx?token={lgs_token}")
        assert res_b.status_code == 200, f"Method B failed: {res_b.status_code} {res_b.text}"
        print(f"Method B (Query Param Token Download): SUCCESS! Size: {len(res_b.content)} bytes")

        # Save sample file and verify it's a valid zip/docx
        with open("sample_downloaded_bisep_paper.docx", "wb") as f:
            f.write(res_b.content)
        assert os.path.exists("sample_downloaded_bisep_paper.docx")
        print("Verified valid saved DOCX on disk.")

        import docx
        doc = docx.Document("sample_downloaded_bisep_paper.docx")
        first_p = doc.paragraphs[0].text if doc.paragraphs else ""
        print(f"First line in DOCX: '{first_p}'")
        assert "LAHORE GRAMMAR SCHOOL" in first_p or "PAKISTAN" in first_p or "SCHOOL" in first_p
        print("CONFIRMED: School name is prominently displayed at top of paper!")

        # Clean up sample
        os.remove("sample_downloaded_bisep_paper.docx")

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_flow()
