""" working with categories of expenses """
from typing import Dict, List, NamedTuple

import db


class Category(NamedTuple):
	""" category structure """
	codename: str
	name: str
	is_base_expense: bool
	aliases: List[str]


class Categories:
	def __init__(self):
		self._categories = self._load_categories()


	def _load_categories(self) -> List[Category]:
		""" returns category dictionary of expenses from DB """
		categories = db.fetchall("category", "codename name is_base_expense aliases".split())
		categories = self._fill_aliases(categories)
		return categories


	def _fill_aliases(self, categories: List[Dict]) -> List[Category]:
		""" fills aliases by every category (or so) """
		categories_result = []
		for index, category in enumerate(categories):
			aliases = category["aliases"].split(",")
			aliases = list(filter(None, map(str.strip, aliases)))
			aliases.append(category["codename"])
			aliases.append(category["name"])

			categories_result.append(Category(codename=category['codename'],
				name=category['name'],
				is_base_expense=category['is_base_expense'],
				aliases=aliases
			))

		return categories_result 


	def get_all_categories(self) -> List[Dict]:
		""" returns dict of categories """
		return self._categories


	def get_category(self, category_name: str) -> Category:
		""" returns category by one of aliases """
		finded = None
		other_category = None

		for category in self._categories:
			if category.codename == "other":
				other_category = category
			for alias in category.aliases:
				if category_name in alias:
					finded = category
		if not finded:
			finded = other_category

		return finded