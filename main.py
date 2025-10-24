import asyncio
from collections import Counter
from collections.abc import Sequence

from fastapi.responses import JSONResponse

from dependency_injection import DependencyContainerBuilder
from models import Notification
from notification_processors import load_notification_processors, NotificationProcessor, ProcessingResult, \
    TelegramConfig, GotifyConfig
from web_application import WebApplicationBuilder, WebApplication


async def process_notification(notification: Notification, processors: tuple[NotificationProcessor]):
    results: Sequence[ProcessingResult] = await asyncio.gather(*(p.process(notification) for p in processors))
    counter = Counter(results)

    return JSONResponse(
        content={"status": f"forwarded '{notification.title}'",
                 "processors": [p.__class__.__name__ for p in processors],
                 "counter": tuple(map(lambda e: e.name, counter.elements())),
                 "fail": counter.get(ProcessingResult.Fail, 0),
                 "skip": counter.get(ProcessingResult.Skip, 0),
                 "success": counter.get(ProcessingResult.Success, 0)},
        status_code=200,
    )


def add_notification_processors_to_di(di: DependencyContainerBuilder):
    processors = load_notification_processors()
    for t in processors:
        di.add_scoped(NotificationProcessor, t)


from configuration import data_providers

if __name__ == "__main__":
    wab: WebApplicationBuilder = WebApplicationBuilder()
    add_notification_processors_to_di(wab.services)

    wab.configuration \
        .add_provider(data_providers.dot_env_file())
    section = wab.configuration.get_section('Gotify')
    wab.configuration.configure(section, GotifyConfig)
    section = wab.configuration.get_section('Telegram')
    wab.configuration.configure(section, TelegramConfig)

    app: WebApplication = wab.build()
    app.map_post('/notify', process_notification) \
        .with_dependencies() \
        .apply()
    app.run()
