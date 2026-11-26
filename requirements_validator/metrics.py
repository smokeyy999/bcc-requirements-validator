"""Run-scoped, content-free transport/usage measurements."""

from contextlib import contextmanager
from contextvars import ContextVar
from threading import Lock
import time


_current = ContextVar("review_metrics", default=None)
_purpose = ContextVar("request_purpose", default="initial")
TOKEN_FIELDS = ("input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens")


class RunMetrics:
    def __init__(self):
        self.started = self.stage_started = time.perf_counter()
        self.stage = "read"
        self.seconds = {}
        self.requests = []
        self.lock = Lock()

    @contextmanager
    def capture(self):
        token = _current.set(self)
        try:
            yield
        finally:
            _current.reset(token)

    def enter(self, name):
        now = time.perf_counter()
        self.seconds[self.stage] = self.seconds.get(self.stage, 0) + now - self.stage_started
        self.stage = name
        self.stage_started = now

    def summary(self):
        now = time.perf_counter()
        stage_seconds = self.seconds.copy()
        stage_seconds[self.stage] = stage_seconds.get(self.stage, 0) + now - self.stage_started
        model = [r for r in self.requests if r["operation"] == "generation"]
        tokens = {}
        coverage = {}
        for field in TOKEN_FIELDS:
            known = [r[field] for r in model if r.get(field) is not None]
            tokens[field] = sum(known) if model and len(known) == len(model) else None
            coverage[field] = {"reporting_calls": len(known), "reported_sum": sum(known) if known else None}
        return {
            "elapsed_seconds": round(now - self.started, 3),
            "stage_seconds": {k: round(v, 3) for k, v in stage_seconds.items()},
            "transport_requests": len(self.requests),
            "model_calls": len(model),
            "successful_model_calls": sum(r["ok"] for r in model),
            "retry_model_calls": sum(r["purpose"] != "initial" or r["transport_attempt"] > 1 for r in model),
            "repair_model_calls": sum(r["purpose"] != "initial" and r["transport_attempt"] == 1 for r in model),
            "transport_retries": sum(r["transport_attempt"] > 1 for r in self.requests),
            "tokens": tokens,
            "token_coverage": coverage,
            "calls_without_io_tokens": sum(r.get("input_tokens") is None or r.get("output_tokens") is None for r in model),
            "cost_usd": None,
            "cost_basis": "Аккаунт не сообщает фактический тариф и начисления за этот запуск.",
            "requests": self.requests,
        }


def stage(name):
    metrics = _current.get()
    if metrics:
        metrics.enter(name)


@contextmanager
def purpose(name):
    token = _purpose.set(name)
    try:
        yield
    finally:
        _purpose.reset(token)


@contextmanager
def transport(operation, attempt=1):
    metrics = _current.get()
    record = {}
    if not metrics:
        yield record
        return
    started = time.perf_counter()
    with metrics.lock:
        record.update(number=len(metrics.requests) + 1, stage=metrics.stage,
                      operation=operation, purpose=_purpose.get(), transport_attempt=attempt, ok=False)
        metrics.requests.append(record)
    try:
        yield record
        record["ok"] = True
    finally:
        record["seconds"] = round(time.perf_counter() - started, 3)


def counts(record, source, fields):
    if isinstance(source, dict):
        for target, reported in fields.items():
            value = source.get(reported)
            if type(value) is int and value >= 0:
                record[target] = value
