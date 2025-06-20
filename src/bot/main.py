import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from .routers import ALL_ROUTERS
from utils import settings, get_redis


async def main():
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await bot.set_my_commands(commands=[
		BotCommand(command="/start", description="Restart bot"),
		BotCommand(command="/genre", description="Set preferred music genre"),
		BotCommand(command="/cancel", description="Cancel current action"),
		BotCommand(command="/support", description="Contact the developer")
	])

    dp = Dispatcher(storage=RedisStorage(await get_redis()))
    dp.include_routers(*ALL_ROUTERS)
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types()
    )

if __name__ == "__main__":
    asyncio.run(main())
