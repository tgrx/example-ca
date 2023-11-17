from typing import Any

import orjson


class AppClientError(RuntimeError):
    def __init__(
        self,
        *args: Any,
        request_body: str | None = None,
        request_headers: dict[str, Any] | None = None,
        request_method: str | None = None,
        request_params: dict[str, Any] | None = None,
        request_path: str | None = None,
        response_body: str | None = None,
        response_code: int | None = None,
        response_headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(*args)
        self.request_body = request_body
        self.request_headers = request_headers
        self.request_method = request_method
        self.request_params = request_params
        self.request_path = request_path
        self.response_body = response_body
        self.response_code = response_code
        self.response_headers = response_headers

    def __str__(self) -> str:
        ctx: dict[str, Any] = {
            "error": super().__str__(),
        }

        if self.request_body:
            ctx.setdefault("request", {})["body"] = self.request_body

        if self.request_headers:
            ctx.setdefault("request", {})["headers"] = self.request_headers

        if self.request_method:
            method = self.request_method.upper()
            ctx.setdefault("request", {})["method"] = method

        if self.request_params:
            ctx.setdefault("request", {})["params"] = self.request_params

        if self.request_path:
            ctx.setdefault("request", {})["path"] = self.request_path

        if self.response_body:
            ctx.setdefault("response", {})["body"] = self.response_body

        if self.response_code:
            ctx.setdefault("response", {})["code"] = self.response_code

        if self.response_body:
            ctx.setdefault("response", {})["body"] = self.response_body

        context_json = orjson.dumps(
            ctx,
            option=orjson.OPT_APPEND_NEWLINE
            | orjson.OPT_INDENT_2
            | orjson.OPT_NON_STR_KEYS
            | orjson.OPT_SERIALIZE_UUID
            | orjson.OPT_SORT_KEYS
            | orjson.OPT_STRICT_INTEGER
            | orjson.OPT_UTC_Z,
        )

        msg = "\n".join(
            filter(
                bool,
                (
                    super().__str__(),
                    "-" * 32,
                    "[context]",
                    context_json.decode(),
                ),
            )
        )

        return msg
