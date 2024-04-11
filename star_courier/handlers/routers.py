"""
Handler routers are defined here.

It is needed to import files which use these routers to initialize endpoints.
"""
from aliceio import Router

echo_router = Router()
ping_router = Router()
start_router = Router()


routers_list = [
    start_router,
    ping_router,
    echo_router
]

__all__ = [
    "routers_list",
]