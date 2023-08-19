import datetime
import asyncio

from interactions.ext.tasks import Trigger

class DateTimeTrigger(Trigger):
    def __init__(self, date: datetime.datetime):
        self.date = date

    async def wait_for_ready(self):
        while datetime.datetime.now() < self.date:
            await asyncio.sleep(1)