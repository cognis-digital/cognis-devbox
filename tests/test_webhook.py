"""Tests for integrations/webhook.py -- error paths and edge cases."""
from __future__ import annotations

import io
import sys
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

# Make the integrations package importable without an __init__.py
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from integrations.webhook import _parse_header, _validate_url, main


# ---------------------------------------------------------------------------
# _validate_url
# ---------------------------------------------------------------------------

class TestValidateUrl:
    def test_valid_https(self):
        assert _validate_url("https://example.com/hook") == "https://example.com/hook"

    def test_valid_http(self):
        assert _validate_url("http://localhost:9000/") == "http://localhost:9000/"

    def test_missing_scheme_raises(self):
        with pytest.raises(ValueError, match="missing a scheme"):
            _validate_url("example.com/hook")

    def test_unsupported_scheme_raises(self):
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            _validate_url("ftp://example.com/hook")

    def test_file_scheme_raises(self):
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            _validate_url("file:///etc/passwd")

    def test_missing_host_raises(self):
        with pytest.raises(ValueError, match="missing a host"):
            _validate_url("https://")


# ---------------------------------------------------------------------------
# _parse_header
# ---------------------------------------------------------------------------

class TestParseHeader:
    def test_simple_header(self):
        k, v = _parse_header("Authorization: Bearer tok")
        assert k == "Authorization"
        assert v == "Bearer tok"

    def test_value_with_colons(self):
        k, v = _parse_header("X-Custom: foo:bar:baz")
        assert k == "X-Custom"
        assert v == "foo:bar:baz"

    def test_no_colon_raises(self):
        with pytest.raises(ValueError, match="missing a colon"):
            _parse_header("BadHeader")

    def test_empty_key_raises(self):
        with pytest.raises(ValueError, match="key is empty"):
            _parse_header(": value")


# ---------------------------------------------------------------------------
# main() -- CLI integration
# ---------------------------------------------------------------------------

def _run_main(args, stdin_text):
    """Run main() with patched sys.argv and sys.stdin."""
    with patch("sys.argv", ["webhook.py"] + args), \
         patch("sys.stdin", io.StringIO(stdin_text)):
        return main()


class TestMainValidation:
    def test_bad_url_scheme_exits_2(self):
        rc = _run_main(["--url", "ftp://example.com/hook"], '{"a": 1}')
        assert rc == 2

    def test_empty_stdin_exits_2(self):
        rc = _run_main(["--url", "https://example.com/hook"], "")
        assert rc == 2

    def test_whitespace_only_stdin_exits_2(self):
        rc = _run_main(["--url", "https://example.com/hook"], "   \n\t")
        assert rc == 2

    def test_malformed_json_stdin_exits_2(self):
        rc = _run_main(["--url", "https://example.com/hook"], "{not json}")
        assert rc == 2

    def test_bad_header_exits_2(self):
        rc = _run_main(
            ["--url", "https://example.com/hook", "--header", "BadHeader"],
            '{"ok": true}',
        )
        assert rc == 2


class TestMainSuccess:
    def _mock_response(self, status=200):
        resp = MagicMock()
        resp.status = status
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    def test_valid_post_returns_0(self, capsys):
        mock_resp = self._mock_response(200)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            rc = _run_main(["--url", "https://example.com/hook"], '{"ok": true}')
        assert rc == 0
        captured = capsys.readouterr()
        assert "posted" in captured.out
        assert "200" in captured.out

    def test_http_error_returns_1(self, capsys):
        err = urllib.error.HTTPError(
            "https://example.com/hook", 403, "Forbidden", {}, None
        )
        with patch("urllib.request.urlopen", side_effect=err):
            rc = _run_main(["--url", "https://example.com/hook"], '{"ok": true}')
        assert rc == 1
        captured = capsys.readouterr()
        assert "403" in captured.err

    def test_url_error_returns_1(self, capsys):
        err = urllib.error.URLError("connection refused")
        with patch("urllib.request.urlopen", side_effect=err):
            rc = _run_main(["--url", "https://example.com/hook"], '{"ok": true}')
        assert rc == 1
        captured = capsys.readouterr()
        assert "webhook error" in captured.err
