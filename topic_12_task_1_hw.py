import pickle

# Клас для зберігання контактів
class AddressBook:
    def __init__(self):
        self.contacts = {}

    def add_contact(self, name, phone):
        self.contacts[name] = phone

    def show_all(self):
        for name, phone in self.contacts.items():
            print(name, ":", phone)


# Збереження книги у файл
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


# Завантаження книги з файлу
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    # Завантажуємо або створюємо нову книгу
    book = load_data()

    while True:
        command = input(">>> ").strip().lower()

        if command == "add":
            name = input("Ім'я: ")
            phone = input("Телефон: ")
            book.add_contact(name, phone)

        elif command == "show":
            book.show_all()

        elif command == "exit":
            save_data(book)
            print("Книга збережена. Вихід...")
            break

        else:
            print("Невідома команда. Використовуйте: add, show, exit")


# Запуск програми
if __name__ == "__main__":
    main()
