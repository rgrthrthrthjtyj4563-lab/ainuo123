import requests
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"

def print_step(step):
    print(f"\n{'='*20} {step} {'='*20}")

def assert_response(response, expected_code, message="Request failed"):
    if response.status_code != expected_code:
        print(f"FAILED: {message} (Status: {response.status_code})")
        print(f"Response: {response.text}")
        sys.exit(1)
    else:
        print(f"PASSED: {message}")

def test_report_structure_module_optimized():
    print("Starting Tests for Optimized Report Structure Module...")

    print_step("1. UI Assertions")
    with open("/Users/lee/Documents/beiyi/爱诺模板项目/frontend/structure-config.html", "r", encoding="utf-8") as f:
        html = f.read()
    forbidden_markers = [
        "添加章节",
        "openChapterModal",
        "saveChapter",
        "fa-grip-vertical",
        "drag-handle",
        "initTreeSortable",
        "saveTreeOrder",
        "/structures/nodes/reorder"
    ]
    for marker in forbidden_markers:
        if marker in html:
            print(f"FAILED: UI contains forbidden marker: {marker}")
            sys.exit(1)
    print("PASSED: UI markers removed")

    print_step("2. Structure APIs")
    payload = {
        "structure_name": f"AutoTest Structure {int(time.time())}",
        "report_type": "doctor",
        "analysis_depth": 3,
        "description": "Optimized module test structure"
    }
    res = requests.post(f"{BASE_URL}/structures", json=payload)
    assert_response(res, 200, "Create structure")
    structure_id = res.json()["data"]["id"]

    res = requests.post(f"{BASE_URL}/structures", json={"report_type": "doctor", "analysis_depth": 3})
    assert_response(res, 422, "Reject invalid structure payload")

    print_step("2.5 Word Extract API")
    word_path = "/Users/lee/Documents/beiyi/爱诺模板项目/test-data/structure-import.docx"
    with open(word_path, "rb") as f:
        res = requests.post(
            f"{BASE_URL}/structures/extract",
            files={"file": ("structure-import.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
    assert_response(res, 200, "Extract structure from Word")
    extracted = res.json().get("data", {}).get("structure", [])
    assert isinstance(extracted, list)
    assert len(extracted) > 0

    print_step("3. Node Creation APIs Removed")
    res = requests.post(f"{BASE_URL}/structures/nodes", json={"structure_id": structure_id})
    assert_response(res, 404, "POST /structures/nodes removed")

    res = requests.post(f"{BASE_URL}/structures/nodes/reorder", json={"items": []})
    assert_response(res, 404, "POST /structures/nodes/reorder removed")

    print_step("4. Import Still Works & Read-only Display OK")
    import_payload = {
        "nodes": [
            {
                "level": 1,
                "node_type": "container",
                "title": "Imported Chapter 1",
                "sort_order": 1,
                "children": [
                    {
                        "level": 2,
                        "node_type": "fixed_content",
                        "title": "Imported Section 1.1",
                        "sort_order": 1,
                        "content_blocks": [{"type": "fixed_intro", "config": {"content": "Hello"}}],
                        "children": []
                    }
                ]
            }
        ]
    }
    res = requests.post(f"{BASE_URL}/structures/{structure_id}/import", json=import_payload)
    assert_response(res, 200, "Import structure nodes")

    res = requests.get(f"{BASE_URL}/structures/{structure_id}")
    assert_response(res, 200, "Get structure detail")
    data = res.json()["data"]
    assert data["id"] == structure_id
    assert len(data["nodes"]) == 1
    assert len(data["nodes"][0]["children"]) == 1
    node_id = data["nodes"][0]["children"][0]["id"]

    print_step("5. Update Node Still Works")
    res = requests.put(
        f"{BASE_URL}/structures/nodes/{node_id}",
        json={"title": "Imported Section 1.1 Updated", "content_blocks": []}
    )
    assert_response(res, 200, "Update node title and blocks")
    assert res.json()["data"]["title"] == "Imported Section 1.1 Updated"

    print_step("6. Cleanup")
    res = requests.delete(f"{BASE_URL}/structures/{structure_id}")
    assert_response(res, 200, "Delete structure")

    print("\nAll tests passed!")

if __name__ == "__main__":
    try:
        test_report_structure_module_optimized()
    except Exception as e:
        print(f"\nTest Execution Failed: {e}")
        sys.exit(1)
