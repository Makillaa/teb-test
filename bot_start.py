import base64
import os
import requests
import re
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from asgiref.sync import sync_to_async
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'teb_test.settings'
django.setup()
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from main.models import TelegramProfile

# create a bot and dispatcher
logging.basicConfig(level=logging.INFO)
API_TOKEN = '6106169030:AAF4t_Uld-WPFsOiPbYJCdJao5v50fkeaTc'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Determining user state
class Registration(StatesGroup):
    username = State()
    first_name = State()
    last_name = State()
    email = State()
    password = State()
    confirm_password = State()


# Checking the entered name
async def validate_name(message: types.Message):
    name = message.text.strip()
    if not name:
        await message.reply("You have not entered a name. Try again.")
        return False
    elif not message.text.strip().isalpha():
        await message.answer("The name must contain only letters. Try again.")
        return False
    return True


# Checking the entered surname
async def validate_surname(message: types.Message):
    surname = message.text.strip()
    if not surname:
        await message.reply("You didn't enter a last name. Try again.")
        return False
    elif not message.text.strip().isalpha():
        await message.answer("Last name must contain only letters. Try again.")
        return False
    return True


# Checking the entered email
async def validate_email(message: types.Message):
    email = message.text.strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await message.reply("Invalid email. Try again.")
        return False
    return True


# Checking the entered password
async def validate_password(message: types.Message):
    password = message.text.strip()
    if len(password) < 8:
        await message.reply("The password must be at least 8 characters long. Try again.")
        return False
    return True


# Check password confirmation
async def validate_confirm_password(message: types.Message, state: FSMContext):
    confirm_password = message.text.strip()
    async with state.proxy() as data:
        if data.get('password') != confirm_password:
            await message.reply("Password mismatch. Try again.")
            return False
    return True


# Getting the account profile
async def get_user_info(user_id):
    chat = await bot.get_chat(user_id)
    return chat


# Loading data from a profile
async def create_profile(user_id, user_inst):
    user_info = await get_user_info(user_id)
    photo = user_info['photo']
    file_id = photo['big_file_id']
    file = await bot.get_file(file_id)
    file_path = file.file_path
    photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    response = requests.get(photo_url)

    if response.status_code == 200:
        image_base64 = base64.b64encode(response.content)

    profile = TelegramProfile(
        user=user_inst,
        first_name=user_info['first_name'],
        username=user_info['username'],
        photo=image_base64,
    )
    await sync_to_async(profile.save)()


# Command handler /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if await sync_to_async(User.objects.filter(username=message.from_user.id).exists)():
        await message.answer("You are already registered. Type /login to log in.\n"
                             "Or use /delete to register again.")
        return
    user_nickname = message.from_user.username
    if user_nickname:
        await message.answer(f"Hi {user_nickname}! Please enter your details to register.\n"
                             "Enter your name:")
    else:
        await message.answer("Hi! Please enter your details to register.\n"
                             "Enter your name:")

    # Go to state "name"
    await Registration.first_name.set()


# Command handler /delete
@dp.message_handler(commands=['delete'])
async def cmd_delete(message: types.Message):
    if await sync_to_async(User.objects.filter(username=message.from_user.id).exists)():
        registration = await sync_to_async(User.objects.get)(username=message.from_user.id)
        await sync_to_async(registration.delete)()
        await message.answer("Registration data deleted successfully.\n"
                             "Use /start to register.")


@dp.message_handler(commands=['login'])
async def cmd_login(message: types.Message):
    await message.answer("To login follow the link:\n"
                         "http://18.195.113.184:8000/login")


# Handler for the entered name
@dp.message_handler(state=Registration.first_name)
async def process_name(message: types.Message, state: FSMContext):
    if await validate_name(message):
        async with state.proxy() as data:
            data['username'] = message.from_user.id
            data['first_name'] = message.text

        await message.answer("Enter your last name:")

        # Go to state "surname"
        await Registration.last_name.set()


# The handler of the entered surname
@dp.message_handler(state=Registration.last_name)
async def process_surname(message: types.Message, state: FSMContext):
    if await validate_surname(message):
        async with state.proxy() as data:
            data['last_name'] = message.text

        await message.answer("Enter your email:")

        # Change to the "email" state
        await Registration.email.set()


# Handler for the entered email
@dp.message_handler(state=Registration.email)
async def process_email(message: types.Message, state: FSMContext):
    if await validate_email(message):
        async with state.proxy() as data:
            data['email'] = message.text

        await message.answer("Enter password:")

        # Change to the "password" state
        await Registration.password.set()


# Entered password handler
@dp.message_handler(state=Registration.password)
async def process_password(message: types.Message, state: FSMContext):
    if await validate_password(message):
        async with state.proxy() as data:
            data['password'] = message.text

        await message.reply("Confirm the password:")

        # Change to the "confirm_password" state
        await Registration.confirm_password.set()


# Password confirmation handler
@dp.message_handler(state=Registration.confirm_password)
async def process_confirm_password(message: types.Message, state: FSMContext):
    if not await validate_confirm_password(message, state):
        async with state.proxy() as data:
            data['password'] = None
            data['confirm_password'] = None
        await message.answer("Re-enter your password:")
        await Registration.password.set()

    elif await validate_confirm_password(message, state):
        async with state.proxy() as data:

            # Create a user
            user = User(
                username=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                password=make_password(data['password'])
            )
            await sync_to_async(user.save)()
            # Create a profile for a user record
            user_inst = await sync_to_async(User.objects.get)(id=user.id)
            await create_profile(data['username'], user_inst)

        await message.answer("You have successfully registered!")

        # Reset user state
        await state.finish()

    else:
        await message.answer("An error occurred while registering, please try again.\n"
                             "To re-register, use /start ")
        await state.finish()
        return


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
