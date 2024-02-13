from dataclasses import dataclass
from typing import Dict, List, Tuple

from django.conf import settings


class HXMessageTags:
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40


@dataclass
class Message:
    body: str
    tags: str

    def __str__(self):
        return self.body


class HXMessages:
    messages: List[Message]
    tags: Dict[int, str]

    def __init__(self) -> None:
        self.messages = []
        self.set_tags()

    def debug(self, message):
        self.messages.append(Message(message, self.tags.get(10)))

    def info(self, message):
        self.messages.append(Message(message, self.tags.get(20)))

    def success(self, message):
        self.messages.append(Message(message, self.tags.get(25)))

    def warning(self, message):
        self.messages.append(Message(message, self.tags.get(30)))

    def error(self, message):
        self.messages.append(Message(message, self.tags.get(40)))

    def set_tags(self):
        if getattr(settings, "HX_REQUESTS_USE_DJANGO_MESSAGE_TAGS", False) is True:
            self.tags = getattr(settings, "MESSAGE_TAGS")
        else:
            self.tags = getattr(settings, "HX_REQUESTS_HX_MESSAGE_TAGS")

        if not self.tags:
            raise Exception(
                "HX_MESSAGE_TAGS must be defined in settings to use messages with hx-requests, or set USE_DJANGO_MESSAGE_TAGS to 'True'."
            )

    def __call__(self):
        if self.messages:
            return self.messages
