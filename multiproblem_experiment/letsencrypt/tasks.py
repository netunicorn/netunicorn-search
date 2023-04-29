
import requests
from returns.result import Success, Failure, Result


def validate_http_01(domain: str, token_name: str, token_data: str) -> Result[None, str]:
    url = f"http://{domain}/.well-known/acme-challenge/{token_name}"
    try:
        response = requests.get(url)
        if response.status_code != 200 or response.content.decode("utf-8") != token_data:
            return Failure(f"HTTP status code {response.status_code}")
        return Success(None)
    except Exception as e:
        return Failure(str(e))
