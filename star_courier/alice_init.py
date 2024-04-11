import os
from aiohttp import web

from aliceio import Dispatcher, Skill
from aliceio.webhook.aiohttp_server import OneSkillRequestHandler, setup_application

from .handlers import list_of_routes


dp = Dispatcher()
dp.include_routers(*list_of_routes)

skill = Skill(skill_id=os.environ.get("ALICE_SKILL_ID"))

app = web.Application()
webhook_requests_handler = OneSkillRequestHandler(
    dispatcher=dp,
    skill=skill,
)

webhook_requests_handler.register(app, path=os.environ.get("WEBHOOK_PATH"))
setup_application(app, dp, skill=skill)