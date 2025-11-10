import asyncio
from collections import Counter
from collections.abc import Sequence

from fastapi.responses import JSONResponse

from dependency_injection import DependencyContainerBuilder
from models import Notification, TrueNasAlert
from notification_publishers import find_notification_publishers, NotificationPublisher, ProcessingResult, \
    TelegramConfig, GotifyConfig
from web_application import WebApplicationBuilder, WebApplication


async def process_notification(notification: Notification, notification_publishers: tuple[NotificationPublisher]):
    results: Sequence[ProcessingResult] = await asyncio.gather(
        *(p.process(notification) for p in notification_publishers)
    )
    counter = Counter(results)

    return JSONResponse(
        content={"status": f"forwarded '{notification.title}'",
                 "processors": [p.__class__.__name__ for p in notification_publishers],
                 "counter": tuple(map(lambda e: e.name, counter.elements())),
                 "fail": counter.get(ProcessingResult.Fail, 0),
                 "skip": counter.get(ProcessingResult.Skip, 0),
                 "success": counter.get(ProcessingResult.Success, 0)},
        status_code=200,
    )


async def process_true_nas_notification(data: TrueNasAlert, notification_publishers: tuple[NotificationPublisher]):
    print(f'Got {data} from TrueNAS')
    notification = Notification(source='truenas', title='Message from TrueNAS', severity='unknown', message=data.text)
    await process_notification(notification, notification_publishers)


def add_notification_processors_to_di(di: DependencyContainerBuilder):
    processors = find_notification_publishers()
    for t in processors:
        di.add_scoped(NotificationPublisher, t)


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
    app.map_post('/truenas-notify', process_true_nas_notification) \
        .with_dependencies() \
        .apply()
    app.run()
