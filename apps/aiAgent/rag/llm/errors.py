"""Provider failures expose status and safe codes, never raw response bodies or keys."""


class LLMError(RuntimeError):
    def __init__(
        self,
        status: int,
        model: str,
        retry_after: float = 0,
        error_code: str | None = None,
        *,
        provider: str,
    ):
        self.status, self.model, self.retry_after = status, model, retry_after
        self.error_code, self.provider = error_code, provider
        self.timings: dict[str, float] = {}
        super().__init__(
            f"{provider} request failed: HTTP {status}, model={model or 'model inventory'}"
        )
