from typing import List, Tuple

from django.conf import settings


class HXMessageTags:
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40


class HXMessages:
    messages: List[Tuple[str, str]]
    # TODO USE json script tag (and use include template for this) and would also need context processr

    tags = ["debug", "info", "success", "warning", "error"]

    def init__(self) -> None:
        self.messages = []
        self.settings_dict = getattr(settings, "HX_REQUESTS_HX_MESSAGES", {})
        tags_mapping = self.get_tags_mapping()

        for tag in self.tags:
            self.tag = lambda message: self.messages.append(
                (message, tags_mapping.get(tag))
            )

    def get_tags_mapping(self):
        if self.settings_dict.get("USE_DJANGO_MESSAGE_TAGS"):
            tags_mapping = getattr(settings, "MESSAGE_TAGS")
        else:
            tags_mapping = self.settings_dict.get("HX_MESSAGE_TAGS")

        if not tags_mapping:
            raise Exception(
                "HX_MESSAGE_TAGS must be defined in settings to use messages with hx-requests."
            )

        new_mapping = {}
        for key, value in tags_mapping:
            if key == 10:
                new_mapping["debug"] = value
            elif key == 20:
                new_mapping["info"] = value
            elif key == 25:
                new_mapping["success"] = value
            elif key == 30:
                new_mapping["warning"] = value
            elif key == 40:
                new_mapping["error"] = value

    def get_message(self):
        if self.messages:
            return self.messages[-1]
