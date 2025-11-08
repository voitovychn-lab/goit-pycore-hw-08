import pickle
from collections import UserDict
from datetime import datetime, date


# -------- Декоратор для обробки помилок користувача --------
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Enter correct data please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter correct arguments."
        except Exception as e:
            return f"Error: {e}"
    return inner


# -------- Класи для структури даних --------
class Field:
    """Базовий клас для всіх полів"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Ім’я контакту"""
    pass


class Phone(Field):
    """Телефон, перевіряє формат (10 цифр)"""
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)


class Birthday(Field):
    """Дата народження у форматі DD.MM.YYYY"""
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    """Описує один контакт: ім’я, телефони, день народження"""
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                if not (new_phone.isdigit() and len(new_phone) == 10):
                    raise ValueError("New phone must contain exactly 10 digits")
                p.value = new_phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    """Клас, який зберігає всі контакти"""
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        """Повертає список контактів з днями народження у найближчі 7 днів"""
        today = date.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.value
                bday_this_year = bday.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                delta = (bday_this_year - today).days
                if delta <= 7:
                    upcoming.append((record.name.value, bday_this_year.strftime("%d.%m.%Y")))
        return upcoming


# -------- Збереження / завантаження даних --------
def save_data(book, filename="addressbook.pkl"):
    """Серіалізація адресної книги у файл"""
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    """Десеріалізація адресної книги з файлу"""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


# -------- Команди CLI-бота --------
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    return f"{name}: {'; '.join(p.value for p in record.phones)}"


@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts found."
    return '\n'.join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.add_birthday(birthday)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    if record.birthday:
        return f"{name}'s birthday is {record.birthday}"
    return "Birthday not found."


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{n}: {d}" for n, d in upcoming)


@input_error
def delete_contact(args, book: AddressBook):
    name = args[0]
    book.delete(name)
    return f"Contact '{name}' deleted if existed."


# -------- Основна логіка програми --------
def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Contacts saved. Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "delete":
            print(delete_contact(args, book))
        else:
            print("Invalid command.")


# -------- Точка входу --------
if __name__ == "__main__":
    main()
