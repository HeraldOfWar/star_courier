from aliceio.types import Message

from .routers import echo_router


@echo_router.message()
async def echo_handler(message: Message) -> str:
    return message.original_text
