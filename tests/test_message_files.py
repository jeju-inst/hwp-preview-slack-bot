"""``_message_files`` looks up the message a file was shared in. Any failure
must return None so the handler falls back to converting (never skips)."""

from hwp_preview_slack_bot.__main__ import _message_files


class _Err(Exception):
    def __init__(self, error):
        super().__init__(error)
        self.response = {"error": error}


class FakeClient:
    def __init__(self, history=None, replies=None, raise_error=None):
        self.history, self.replies, self.raise_error = history, replies, raise_error
        self.calls = []

    def conversations_history(self, **kw):
        self.calls.append(("history", kw))
        if self.raise_error:
            raise _Err(self.raise_error)
        return {"messages": self.history or []}

    def conversations_replies(self, **kw):
        self.calls.append(("replies", kw))
        if self.raise_error:
            raise _Err(self.raise_error)
        return {"messages": self.replies or []}


FILES = [{"name": "a.hwpx"}, {"name": "a.pdf"}]


def _info(entry, scope="public"):
    return {"shares": {scope: {"C1": [entry]}}}


def test_channel_message_via_history():
    c = FakeClient(history=[{"ts": "1.1", "files": FILES}])
    assert _message_files(c, "C1", _info({"ts": "1.1"})) == FILES
    assert c.calls[0][0] == "history"


def test_thread_reply_via_replies():
    c = FakeClient(replies=[{"ts": "1.0"}, {"ts": "1.5", "files": FILES}])
    info = _info({"ts": "1.5", "thread_ts": "1.0"}, scope="private")
    assert _message_files(c, "C1", info) == FILES
    assert c.calls[0][0] == "replies"
    assert c.calls[0][1]["ts"] == "1.0"


def test_lookup_error_returns_none():
    c = FakeClient(raise_error="not_in_channel")
    assert _message_files(c, "C1", _info({"ts": "1.1"})) is None


def test_message_missing_returns_none():
    c = FakeClient(history=[{"ts": "9.9", "files": FILES}])
    assert _message_files(c, "C1", _info({"ts": "1.1"})) is None


def test_no_share_returns_none_without_calling_api():
    c = FakeClient()
    assert _message_files(c, "C1", {"shares": {}}) is None
    assert _message_files(c, "C1", {}) is None
    assert c.calls == []
