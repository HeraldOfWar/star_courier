from aliceio import F
from aliceio.types import AliceResponse, Message, Response

from .routers import start_router


@start_router.message(F.session.new)  # О фильтрах в следующей главе
async def start_handler(message: Message) -> AliceResponse:
    return AliceResponse(response=Response(text="Привет! Внимательно слушаю"))
