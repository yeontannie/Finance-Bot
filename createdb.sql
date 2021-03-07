create table budget(
	codename varchar(255) primary key,
	weekly_limit integer);

create table category(
	codename varchar(255) primary key,
	name varchar(255),
	is_base_expense boolean,
	aliases text);

create table expense(
	id integer primary key,
	amount integer,
	created datetime,
	category_codename integer,
	raw_text text,
	FOREIGN KEY(category_codename) REFERENCES category(codename));

insert into category (codename, name, is_base_expense, aliases)
values
	("products", "продукти", true, "їжа"),
	("coffee", "кава", true, "чай"),
	("dinner", "обід", true, "ланч"),
	("cafe", "кафе", true, "ресторан, мак, kfc"),
	("transport", "bus", "транспорт", false, "метро, автобус"),
	("taxi", "таксі", false, ""),
	("phone", "телефон", false, "зв'язок"),
	("books", "книги", false, "література, літ-ра, книжки, книжка"),
	("internet", "інтернет", false, "інет, inet"),
	("other", "інше", true, "");

insert into budget(codename, weekly_limit) values ('base', 500);
