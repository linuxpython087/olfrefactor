class EventBus:
    def __init__(self):
        self.handlers = {}

    def register(self, event, handler):
        self.handlers.setdefault(event, []).append(handler)

    def publish(self, event):
        for handler in self.handlers.get(type(event), []):
            handler(event)
