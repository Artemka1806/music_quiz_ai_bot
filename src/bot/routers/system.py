from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start_command_handler(message: Message):
    await message.answer("Hello world!")


@router.message(Command("support"))
async def support_command_handler(message: Message):
    await message.answer("Developer: @Artemka1806")
