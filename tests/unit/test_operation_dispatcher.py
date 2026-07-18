"""Tests for step dispatcher."""

import pytest

from dav_platform.core.contracts import ExecutionStep
from dav_platform.operations.dispatcher import (
    register_handler,
    get_handler,
    clear_handlers,
    dispatch_step,
)


class TestDispatcher:
    def setup_method(self):
        clear_handlers()

    def teardown_method(self):
        clear_handlers()

    def test_register_and_get_handler(self):
        def my_handler(step=None, dataset=None, context=None, options=None):
            return "ok"

        register_handler("test_action", my_handler)
        handler = get_handler("test_action")
        assert handler is not None
        assert handler(step=None) == "ok"

    def test_get_unknown_handler(self):
        assert get_handler("unknown") is None

    def test_dispatch_step(self):
        def my_handler(step, dataset=None, context=None, options=None):
            return {"status": "done"}

        register_handler("load", my_handler)
        step = ExecutionStep(step_number=1, action="load", description="Load data")
        result = dispatch_step(step, dataset="data", context="ctx")
        assert result == {"status": "done"}

    def test_dispatch_unknown_action(self):
        step = ExecutionStep(step_number=1, action="unknown", description="Unknown")
        with pytest.raises(ValueError, match="No handler"):
            dispatch_step(step)

    def test_clear_handlers(self):
        register_handler("test", lambda **kw: None)
        clear_handlers()
        assert get_handler("test") is None
