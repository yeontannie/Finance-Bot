#!/usr/bin/python3.9

""" Server for tg bot"""
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, executor, types

import exceptions
import expenses
from categories import Categories

#GLOBAL CONSTANTS
API_TOKEN = ''

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
	"""	Send welcome message and help info about bot"""
	await message.answer(
		"Bot for finance tracking\n\n"
		"Can add expences: 15 bus\n"
		"Today statistics: /today\n"
		"Month statistics: /month\n"
		"Last expenses: /expenses\n"
		"Categories: /categories")


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
	""" Delete one record about expence by id"""
	row_id = int(message.text[4:])
	expenses.delete_expense(row_id)
	answer_message = "Deleted"
	await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
	""" Send list of categories of expenses"""
	categories = Categories().get_all_categories()
	answer_message = "Categories of expences: \n\n* " +\
	("\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
	await message.answer(answer_message)


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
	""" Send today's expences"""
	answer_message = expenses.get_today_statistics()
	await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
	""" Send month's statistics"""
	answer_message = expenses.get_month_statistics()
	await message.answer(answer_message)


@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
	""" Send record of last expences"""
	last_expenses = expenses.last()
	if not last_expenses:
		await message.answer("No expenses yet")
		return

	last_expenses_rows = [
		f"{expense.amount} uah. on {expense.category_name} - tap  "
		f"/del{expense.id} to delete"
		for expense in last_expenses]

	answer_message = "Last saved expenses: \n\n* " + "\n\n* ".join(last_expenses_rows)

	await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
	""" Add new expense"""
	try:
		expense = expenses.add_expense(message.text)
	except exceptions.NotCorrectMessage as e:
		await message.answer(str(e))
		return
	answer_message = (
		f"Added expenses {expense.amount} uah. on {expense.category_name}.\n\n"
		f"{expenses.get_today_statistics()}")
	await message.answer(answer_message)


if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=True)
