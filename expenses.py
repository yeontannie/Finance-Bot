""" Working with expenses: add, delete, statistic"""
import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
import exceptions
from categories import Categories


class Message(NamedTuple):
	""" Structure of parsed message about new expense"""
	amount: int
	category_text: str


class Expense(NamedTuple):
	""" Structure of expense, which added ro DB"""
	id: Optional[int]
	amount: int
	category_name: str


def add_expense(raw_message: str) -> Expense:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(
        parsed_message.category_text)
    inserted_row_id = db.insert("expense", {
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Expense(id=None,
                   amount=parsed_message.amount,
                   category_name=category.name)


def get_today_statistics() -> str:
	""" returns statistics of expenses for today"""
	cursor = db.get_cursor()
	cursor.execute("select sum(amount)"
		"from expense where date(created)=date('now', 'localtime')")
	result = cursor.fetchone()
	if not result[0]:
		return "No expenses for today"
	all_today_expenses = result[0]
	cursor.execute("select sum(amount)"
		"from expense where date(created)=date('now', 'localtime')"
		"and category_codename in (select codename "
		"from category where is_base_expense=true)")

	result = cursor.fetchone()
	base_today_expenses = result[0] if result[0] else 0
	return (f"Expenses today:\n"
		f"Total - {all_today_expenses} uah.\n"
		f"Base - {base_today_expenses} uah. out of {_get_budget_limit()/10} uah.\n\n"
		f"Month expenses:  /month")


def get_month_statistics() -> str:
	""" returns statistics of month expenses as string"""
	now = _get_now_datetime()
	first_day_of_month = f"{now.year:04d}-{now.month:02d}-01"
	cursor = db.get_cursor()
	cursor.execute(f"select sum(amount)"
		f"from expense where date(created) >= '{first_day_of_month}'")

	result = cursor.fetchone()
	if not result[0]:
		return "No expenses for this month"
	all_today_expenses = result[0]
	cursor.execute(f"select sum(amount)"
		f"from expense where date(created) >= '{first_day_of_month}'"
		f"and category_codename in (select codename "
		f"from category where is_base_expense=true)")

	result = cursor.fetchone()
	base_today_expenses = result[0] if result[0] else 0
	return (f"Current month expenses:\n"
		f"Total - {all_today_expenses} uah. \n"
		f"Base - {base_today_expenses} uah. out of "
		f"{_get_budget_limit()} uah.")
#now.day *

def last() -> List[Expense]:
    """Returns a couple of last expenses"""
    cursor = db.get_cursor()
    cursor.execute(
        "select e.id, e.amount, c.name "
        "from expense e left join category c "
        "on c.codename=e.category_codename "
        "order by created desc limit 10")
    rows = cursor.fetchall()
    last_expenses = [Expense(id=row[0],  amount=row[1], category_name=row[2]) for row in rows]
    return last_expenses


def delete_expense(row_id: int) -> None:
    """Deletes messages by id"""
    db.delete("expense", row_id)


def _parse_message(raw_message: str) -> Message:
    """Parsing text of message about new expense"""
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Can't understand message. Write in format, "
            "example:\n15 coffee")

    amount = regexp_result.group(1).replace(" ", "")
    category_text = regexp_result.group(2).strip().lower()
    return Message(amount=amount, category_text=category_text)


def _get_now_formatted() -> str:
	""" returns todays date as str """
	return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
	""" returns todays datetime considering time zone (Kiev) """
	tz = pytz.timezone("Europe/Kiev")
	now = datetime.datetime.now(tz)
	return now


def _get_budget_limit() -> int:
	""" returns limit of budget for week """
	return db.fetchall("budget", ["weekly_limit"])[0]["weekly_limit"]
