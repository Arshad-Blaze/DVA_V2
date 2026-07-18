"""Step dispatcher — routes execution steps to correct downstream layers."""

from typing import Any, Callable, Dict, Optional

from dav_platform.core.contracts import ExecutionStep


# Registry of step handlers
_handlers: Dict[str, Callable] = {}


def register_handler(action: str, handler: Callable):
    """Register a handler for a step action.

    Args:
        action: Step action name (e.g., 'aggregate', 'validate', 'report')
        handler: Callable that executes the step
    """
    _handlers[action] = handler


def get_handler(action: str) -> Optional[Callable]:
    """Get handler for a step action."""
    return _handlers.get(action)


def clear_handlers():
    """Clear all registered handlers (for testing)."""
    _handlers.clear()


def dispatch_step(
    step: ExecutionStep,
    dataset: Any = None,
    context: Any = None,
    options: Optional[Dict] = None,
) -> Any:
    """Dispatch a step to its registered handler.

    Args:
        step: The execution step to dispatch
        dataset: The canonical dataset
        context: The operation context
        options: Additional options

    Returns:
        Result from the handler

    Raises:
        ValueError: No handler registered for this action
    """
    handler = get_handler(step.action)
    if handler is None:
        raise ValueError(f"No handler registered for action: {step.action}")

    return handler(step=step, dataset=dataset, context=context, options=options or {})
