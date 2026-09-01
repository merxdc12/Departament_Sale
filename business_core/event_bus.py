"""Small in-process event bus for deterministic department communication.

No external publishing, spending or platform actions happen here. The bus only
routes internal business events to registered handlers.
"""

from collections import defaultdict
from collections.abc import Callable

from .events import BusinessEvent, EventName

EventHandler = Callable[[BusinessEvent], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._history: list[BusinessEvent] = []

    def subscribe(self, event_name: EventName, handler: EventHandler) -> None:
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: EventName, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_name, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: BusinessEvent) -> None:
        self._history.append(event)
        for handler in tuple(self._handlers.get(event.name, ())):
            handler(event)

    @property
    def history(self) -> tuple[BusinessEvent, ...]:
        return tuple(self._history)
