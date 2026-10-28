"""Provider failures expose status and safe codes, never raw response bodies or keys."""


def transport_error_code(error: Exception) -> str:
    reason = getattr(error, "reason", error)
    return "transport_timeout" if isinstance(reason, TimeoutError) else "transport_connection_error"


class ContractIssue(str):
    """String-compatible diagnostic with typed repair data, never executable instructions."""

    diagnostic: dict

    def __new__(cls, message: str, *, code: str, path: str, expected=None, actual=None):
        value = super().__new__(cls, message)
        from rag.llm.contracts.diagnostics import metadata

        value.diagnostic = {
            **metadata(code),
            "code": code,
            "path": path,
            "message": message,
            "expected": expected,
            "actual": actual,
        }
        return value

    def __deepcopy__(self, memo):
        from copy import deepcopy

        detail = deepcopy(self.diagnostic, memo)
        return type(self)(
            str(self),
            code=detail["code"],
            path=detail["path"],
            expected=detail.get("expected"),
            actual=detail.get("actual"),
        )


class RequestPlanError(ValueError):
    error_code = "INVALID_REQUEST_PLAN"


def scoped_issue(error: str, result_id: str) -> str:
    if isinstance(error, ContractIssue):
        detail = error.diagnostic
        return ContractIssue(
            f"{result_id}: {error}",
            code=detail["code"],
            path=f"{result_id}/{detail['path']}",
            expected=detail["expected"],
            actual=detail["actual"],
        )
    return f"{result_id}: {error}"


class LLMError(RuntimeError):
    def __init__(
        self,
        status: int,
        model: str,
        retry_after: float = 0,
        error_code: str | None = None,
        *,
        provider: str,
        message: str | None = None,
    ):
        self.status, self.model, self.retry_after = status, model, retry_after
        self.error_code, self.provider, self.error_message = error_code, provider, message
        self.timings: dict[str, float] = {}
        self.transport_attempts: list[dict] = []
        detail = f": {message}" if message else ""
        super().__init__(
            f"{provider} request failed: HTTP {status}, model={model or 'model inventory'}{detail}"
        )
