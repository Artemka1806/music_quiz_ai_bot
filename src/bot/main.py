import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from .routers import ALL_ROUTERS
from utils import settings, get_redis
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def main():
    logger.info("Starting Music Quiz Bot")
    try:
        bot = Bot(
            token=settings.BOT_TOKEN.get_secret_value(),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        logger.info("Bot instance created successfully")

        await bot.set_my_commands(commands=[
            BotCommand(command="/start", description="Restart bot"),
            BotCommand(command="/genre", description="Set preferred music genre"),
            BotCommand(command="/cancel", description="Cancel current action"),
            BotCommand(command="/support", description="Contact the developer")
        ])
        logger.debug("Bot commands registered")

        redis = await get_redis()
        dp = Dispatcher(storage=RedisStorage(redis))
        logger.info("Dispatcher initialized with Redis storage")

        dp.include_routers(*ALL_ROUTERS)
        logger.debug("All routers included")

        logger.info("Starting bot polling")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    except Exception as e:
        logger.critical(f"Failed to start bot: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}")
        raise
