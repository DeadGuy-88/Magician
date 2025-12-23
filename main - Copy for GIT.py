import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
import funcs
import emoji

TOKEN = "" # YOUR TG BOT TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher()

class TicketState(StatesGroup):
    add_extra = State()
    waiting_for_text = State()


# All of the work is initiated by /start command
# There is a keyboard for sending new ticket and viewing the your last
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Send ticket", callback_data="send_ticket")],
            [InlineKeyboardButton(text="View my last ticket", callback_data="view_last_ticket")],
        ])
    await message.answer("How can I help you?", reply_markup=keyboard)


# Callback for sending the ticket sets the state and moving forward...
@dp.callback_query(F.data == "send_ticket")
async def process_ticket(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(TicketState.waiting_for_text)
    await callback.message.delete()
    await callback.message.answer("Tell us about your problem.")
    await callback.answer()

# Callback for adding extra for your last ticket and moving forward...
@dp.callback_query(F.data == "ticket_add_extra")
async def ticket_add_extra(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(TicketState.add_extra)
    await callback.message.delete()
    await callback.message.answer("Tell us what you want to add.")
    await callback.answer()

# Callback for viewing your last ticket. Not moving forward, all of it is here.
@dp.callback_query(F.data == "view_last_ticket")
async def view_last_ticket(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    last_ticket = funcs.get_last_users_ticket(callback.from_user.username) # Функций из файла funcs, которая находит последний тикет юзера
    if last_ticket is None:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Send ticket", callback_data="send_ticket")],
            ])
        await callback.message.answer("You have no tickets at the moment.", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard = [
                [InlineKeyboardButton(text="Add extra", callback_data="ticket_add_extra")],
            ])
        await callback.message.answer(f"Your lastest ticket:\n {last_ticket}", reply_markup=keyboard)
        await callback.answer()



# Script for adding extra information to your last ticket
@dp.message(TicketState.add_extra)
async def handle_ticket_add_extra(message: types.Message, state: FSMContext):
    def is_not_text(message: types.Message) -> bool: # Проверяем, текст ли это вообще
        return message.text is None
    if is_not_text(message):
        await message.reply("Sorry, but I don't understand you. Please try again.")
        await state.set_state(TicketState.waiting_for_text)
    else:
        cleaned_text = emoji.replace_emoji(message.text, replace="")
        funcs.add_extra_to_tickets(str(message.chat.id),str(message.from_user.username), cleaned_text)
        await message.answer("Thank you! We received your ticket.")
    await state.clear()


# Script to send a new ticket to db
@dp.message(TicketState.waiting_for_text)
async def handle_ticket_text(message: types.Message, state: FSMContext):
    def is_not_text(message: types.Message) -> bool: # Проверяем, текст ли это вообще
        return message.text is None
    if is_not_text(message):
        await message.reply("Sorry, but I don't understand you. Please try again.")
        await state.set_state(TicketState.waiting_for_text)
    else:
        cleaned_text = emoji.replace_emoji(message.text, replace="")
        if funcs.check_existing_tickets(str(message.from_user.username), cleaned_text):
            await message.answer("Your ticket has already been received.")
        elif not funcs.check_existing_tickets(str(message.from_user.username), cleaned_text):
            funcs.ticket_to_db(str(message.chat.id),str(message.from_user.username),cleaned_text)
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="View my last ticket", callback_data="view_last_ticket")],
                ])
            await message.answer("Thank you! We received your ticket.",reply_markup=keyboard)
            await bot.send_message('360749293', "New ticket arrived!")
            await bot.forward_message('360749293', message.chat.id, message.message_id)
        await state.clear()


@dp.message()
async def fallback(message: types.Message):
    await message.answer("Please press /start to send a ticket.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())