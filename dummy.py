import requests

class SimpleHttpClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, params=None, headers=None):
        response = requests.get(f"{self.base_url}/{endpoint}", params=params, headers=headers)
        return self._handle_response(response)

    def post(self, endpoint, data=None, json=None, headers=None):
        response = requests.post(f"{self.base_url}/{endpoint}", data=data, json=json, headers=headers)
        return self._handle_response(response)

    def put(self, endpoint, data=None, headers=None):
        response = requests.put(f"{self.base_url}/{endpoint}", data=data, headers=headers)
        return self._handle_response(response)

    def delete(self, endpoint, headers=None):
        response = requests.delete(f"{self.base_url}/{endpoint}", headers=headers)
        return self._handle_response(response)

    def _handle_response(self, response):
        response.raise_for_status()  # Raises an error for non-200 responses
        return response.json()  # Parses JSON response

# Usage example:
client = SimpleHttpClient("http://localhost:9000")
result = client.get("products/observer/1")
print(result)
