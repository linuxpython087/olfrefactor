# backend/contenu/core/application/events.py
from typing import Callable

from contenu.core.domaine.events import *


class EventDispatcher:
    """Dispatcher central pour tous les DomainEvents."""

    # Mapping type d'événement → fonction à appeler
    _handlers: dict[type, list[Callable]] = {}

    @classmethod
    def register(cls, event_type: type, handler: Callable):
        """Enregistre un handler pour un type d'événement."""
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []
        cls._handlers[event_type].append(handler)

    @classmethod
    def dispatch(cls, event: DomainEvent):
        """Dispatch un événement à tous les handlers enregistrés."""

        handlers = cls._handlers.get(type(event), [])
        for handler in handlers:
            handler(event)
