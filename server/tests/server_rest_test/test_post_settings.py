import requests
import settings
import json

def test_post_settings_success():
    url = settings.API_URL + "settings"
    headers = {
        "user-agent": "vscode-restclient",
        "content-type": "application/json"
    }
    
    # Example settings data - adjust according to your actual settings structure
    new_settings = {
        "settings": {
            "harvest": {
                "endpoints": ["https://example.com/harvest"]
            }
        }
    }

    response = requests.post(url, json=new_settings, headers=headers, timeout=settings.REQUEST_TIMEOUT)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    try:
        json_response = response.json()
        assert isinstance(json_response, dict)
        assert "success" in json_response
        assert json_response["success"] is True
    except json.JSONDecodeError:
        assert False, "Response is not valid JSON"

# def test_post_settings_invalid_json():
#     url = settings.API_URL + "settings"
#     headers = {
#         "user-agent": "vscode-restclient",
#         "content-type": "application/json"
#     }
    
#     invalid_json = "{invalid json}"

#     response = requests.post(url, data=invalid_json, headers=headers, timeout=settings.REQUEST_TIMEOUT)

#     assert response.status_code == 400
#     assert response.headers["content-type"] == "application/json"

#     try:
#         json_response = response.json()
#         assert isinstance(json_response, dict)
#         assert "error" in json_response
#     except json.JSONDecodeError:
#         assert False, "Response is not valid JSON"

# def test_post_settings_invalid_structure():
#     url = settings.API_URL + "settings"
#     headers = {
#         "user-agent": "vscode-restclient",
#         "content-type": "application/json"
#     }
    
#     invalid_structure = {
#         "invalid_key": "invalid_value"
#     }

#     response = requests.post(url, json=invalid_structure, headers=headers, timeout=settings.REQUEST_TIMEOUT)

#     assert response.status_code in [400, 422]  # Depending on how your API handles validation errors
#     assert response.headers["content-type"] == "application/json"

#     try:
#         json_response = response.json()
#         assert isinstance(json_response, dict)
#         assert "error" in json_response
#     except json.JSONDecodeError:
#         assert False, "Response is not valid JSON"