"""Security/concurrency primitives for the localhost candidate dashboard."""
from __future__ import annotations
from pathlib import Path, PureWindowsPath
from threading import RLock
from urllib.parse import urlparse

LOCAL_HOSTS = {"127.0.0.1", "localhost", "[::1]", "::1"}


def validated_relative_path(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("Path must be a safe relative path.")
    native, windows = Path(value), PureWindowsPath(value)
    if native.is_absolute() or native.drive or windows.is_absolute() or windows.drive:
        raise ValueError("Path must be a safe relative path.")
    if ".." in native.parts or ".." in windows.parts:
        raise ValueError("Path must be a safe relative path.")
    return native


def local_request_allowed(*, host_header: str | None, origin_header: str | None) -> bool:
    """Reject obvious DNS-rebinding/cross-origin mutations while keeping local CLI/browser use simple."""
    if not host_header:
        return False
    host = host_header.rsplit(":", 1)[0] if host_header.count(":") <= 1 else host_header
    if host not in LOCAL_HOSTS:
        return False
    if not origin_header:
        return True
    try:
        origin = urlparse(origin_header)
    except ValueError:
        return False
    return origin.scheme == "http" and origin.hostname in {"127.0.0.1", "localhost", "::1"}


class MutationLock:
    """Process-local serialization for dashboard read-modify-write mutations."""
    def __init__(self) -> None:
        self._lock = RLock()
    def __enter__(self):
        self._lock.acquire()
        return self
    def __exit__(self, exc_type, exc, tb):
        self._lock.release()
        return False
