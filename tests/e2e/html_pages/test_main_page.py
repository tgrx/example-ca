import hashlib

from httpx import Client
from httpx import Response


def test_main_page_is_available(*, web_browser: Client) -> None:
    response = web_browser.get("/")
    assert_page_is_avaliable(response)
    assert_page_content_is_valid(response.text)


def assert_page_is_avaliable(response: Response, /) -> None:
    assert response.status_code == 200, "page on / is not available"


def assert_page_content_is_valid(page: str, /) -> None:
    hasher = hashlib.sha224()
    hasher.update(page.encode())

    expected = "e4bfcae3d7e8c5e362e59de2646cab4c710ce8ef09d6c543f71187d3"
    assert hasher.hexdigest() == expected, "modified page content"
