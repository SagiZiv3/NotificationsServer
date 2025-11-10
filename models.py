from pydantic import BaseModel


class Notification(BaseModel):
    source: str
    title: str
    severity: str
    message: str

class TrueNasAlert(BaseModel):
    text: str
