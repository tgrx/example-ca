from typing import Any

import orjson


class AppClientError(RuntimeError):
    def __init__(
        self,
        *args: Any,
        code: int | None = None,
        headers: dict | None = None,
        payload: str | None = None,
    ) -> None:
        super().__init__(*args)
        self.code = code
        self.payload = payload
        self.headers = headers

    def __str__(self) -> str:
        context = {
            "code": self.code,
            "headers": self.headers,
            "payload": self.payload,
        }

        context_json = orjson.dumps(
            context,
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
