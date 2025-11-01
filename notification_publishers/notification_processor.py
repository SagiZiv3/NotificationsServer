from models import Notification


def get_short_message(notification: Notification) -> str:
    match notification.source:
        case 'proxmox':
            return _processes_proxmox_notification_message(notification.message)
        case _:
            return notification.message


def _processes_proxmox_notification_message(notification_message: str) -> str:
    details_header = '[Details]'
    if details_header not in notification_message:
        return notification_message

    details_start_index = notification_message.index(details_header) + len(details_header)
    details_end_index = notification_message.index('[Logs]', details_start_index)

    return notification_message[details_start_index:details_end_index].strip()
