from typing import Any

import httpx

from app.config import get_rsa_api_base_url


class RSAClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, timeout: float = 30.0) -> None:
        self.base_url = (base_url or get_rsa_api_base_url()).rstrip("/")
        self.timeout = timeout

    def search_doctors_or_clinic(self, query: str) -> dict[str, Any]:
        data = self._request("GET", "/", params={"action": "search", "q": query})
        return data.get("results", [])

    def get_nearest_schedules_by_location_id(self, location_id: str) -> dict[str, Any]:
        data= self._request("GET", "/", params={"action": "nearest", "location_id": location_id})
        return data.get("schedules", [])

    def get_schedules_by_date_and_optional_query(self, date: str, query: str | None = None) -> dict[str, Any]:
        params = {"date": date}
        if query is not None:
            params["q"] = query
        data = self._request("GET", "/", params=params)
        return data.get("schedules", {})

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.base_url:
            return {}

        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.request(method, path, params=params)
            response.raise_for_status()
        return response.json()
