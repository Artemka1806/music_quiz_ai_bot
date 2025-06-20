from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.utils.ai import MusicQuizAI
from src.utils.settings import settings

router = Router()
ai = MusicQuizAI(api_key=settings.GEMINI_API_KEY)

@router.message(F.text)
async def handle_answer(message: Message, state: FSMContext, bot: Bot):
    await bot.send_chat_action(message.chat.id, "typing", request_timeout=10)

    data = await state.get_data()
    correct_answer = data.get("correct_answer")
    
    if not correct_answer:
        await message.answer("Please start the quiz with /start command")
        return
    
    is_correct = message.text == correct_answer
    response = "✅ Correct! Let's try another one!" if is_correct else f"❌ Wrong! The correct answer was: {correct_answer}"
    
    quiz_response = await ai.generate_question()
    new_correct_answer = next(option.text for option in quiz_response.options if option.is_correct)
    await state.update_data(correct_answer=new_correct_answer)
    
    question_text = f"{response}\n\n🎵 {quiz_response.question}\n\n"
    if quiz_response.hint:
        question_text += f"\n💡 Hint: <tg-spoiler>{quiz_response.hint}</tg-spoiler>"
    
    builder = ReplyKeyboardBuilder()
    for option in quiz_response.options:
        builder.add(KeyboardButton(text=option.text))
    builder.adjust(1)
    keyboard = builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Select answer"
    )
    
    await message.answer(
        text=question_text,
        reply_markup=keyboard
    )
