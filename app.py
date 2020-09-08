from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    UserState,
    TurnContext
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity

from config import DefaultConfig
from welcome import  WelcomeBot
from dialog import SmartBot

from adapter_with_error_handler import AdapterWithErrorHandler

CONFIG = DefaultConfig()
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

# Create adapter
botadaptersettings = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
botadapter = AdapterWithErrorHandler(botadaptersettings, CONVERSATION_STATE)

# Create dialogs and Bot
WELCOME = WelcomeBot()
BOT = SmartBot()

# Listen for incoming requests on /api/messages.
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    await botadapter.process_activity(activity, auth_header, WELCOME.on_turn)
    response = await botadapter.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=201)


app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages)


web.run_app(app, host="localhost", port=CONFIG.PORT)