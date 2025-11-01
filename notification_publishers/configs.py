from typing import NamedTuple


class GotifyConfig(NamedTuple):
    server_url: str
    general_api_token: str
    api_token_per_source: dict[str, str]


class TelegramConfig(NamedTuple):
    bot_token: str
    chat_id: str
