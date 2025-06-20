from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.utils.ai import MusicQuizAI
from src.utils.settings import settings
from src.utils.r import get_redis

router = Router()
ai = MusicQuizAI(api_key=settings.GEMINI_API_KEY)

class QuizStates(StatesGroup):
    answering = State()
    selecting_genre = State()
    entering_custom_genre = State()

AVAILABLE_GENRES = [
    "Rock", "Pop", "Hip Hop", "Jazz", "Classical",
    "Electronic", "R&B", "Country", "Metal", "Folk"
]


@router.message(Command("genre"))
async def genre_command_handler(message: Message, state: FSMContext):
    await state.set_state(QuizStates.selecting_genre)
    builder = ReplyKeyboardBuilder()
    for genre in AVAILABLE_GENRES:
        builder.add(KeyboardButton(text=f"🎵 {genre}"))
    builder.add(KeyboardButton(text="🎼 Custom Genre"))
    builder.adjust(2)
    keyboard = builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Select genre"
    )
    
    await message.answer(
        "Please select a music genre for your quiz questions, or choose 'Custom Genre' to enter your own:\n\nYou can use /cancel to stop genre selection at any time.",
        reply_markup=keyboard
    )


@router.message(QuizStates.selecting_genre, F.text.startswith("🎵 "))
async def handle_genre_selection(message: Message, state: FSMContext):
    genre = message.text[2:].strip()  # Remove the 🎵 emoji
    redis = await get_redis()
    await redis.set(f"user:{message.from_user.id}:genre", genre)
    await state.clear()
    
    await message.answer(
        f"Great! Your preferred genre is set to {genre}. Use /start to begin the quiz with this genre!",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(QuizStates.selecting_genre, F.text == "🎼 Custom Genre")
async def ask_custom_genre(message: Message, state: FSMContext):
    await state.set_state(QuizStates.entering_custom_genre)
    await message.answer(
        "Please enter your preferred music genre:",
        reply_markup=ReplyKeyboardBuilder().as_markup(resize_keyboard=True)
    )


@router.message(QuizStates.entering_custom_genre)
async def handle_custom_genre(message: Message, state: FSMContext):
    genre = message.text.strip()
    redis = await get_redis()
    await redis.set(f"user:{message.from_user.id}:genre", genre)
    await state.clear()
    
    await message.answer(
        f"Great! Your preferred genre is set to {genre}. Use /start to begin the quiz with this genre!",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(CommandStart())
async def start_command_handler(message: Message, state: FSMContext, bot: Bot):
    await bot.send_chat_action(message.chat.id, "typing", request_timeout=10)
    
    redis = await get_redis()
    genre = await redis.get(f"user:{message.from_user.id}:genre")
    
    quiz_response = await ai.generate_question(genre=genre)
    correct_answer = next(option.text for option in quiz_response.options if option.is_correct)
    
    await state.set_state(QuizStates.answering)
    await state.update_data(correct_answer=correct_answer)
    
    response_text = f"🎵 {quiz_response.question}\n\n"
    
    if quiz_response.hint:
        response_text += f"\n💡 Hint: <tg-spoiler>{quiz_response.hint}</tg-spoiler>"
    
    if not genre:
        response_text += "\n\n📌 Tip: Use /genre to set your preferred music genre!"
    
    builder = ReplyKeyboardBuilder()
    for option in quiz_response.options:
        builder.add(KeyboardButton(text=option.text))
    builder.adjust(1)
    keyboard = builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Select answer"
    )

    await message.answer(
        text=response_text,
        reply_markup=keyboard
    )


@router.message(Command("support"))
async def support_command_handler(message: Message):
    await message.answer("Developer: @Artemka1806")


@router.message(Command("cancel"))
async def cancel_command_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Current action cancelled. Use /start for a new question or /genre to set your preferred genre.",
        reply_markup=ReplyKeyboardRemove()
    )
