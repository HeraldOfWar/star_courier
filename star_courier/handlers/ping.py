from aliceio import F
from aliceio.types import Message, Response

from .routers import ping_router


@ping_router.message(F.command == "ping")
@ping_router.message(F.command == "пинг")
async def echo_handler(message: Message) -> Response:
    return Response(text="понг")
