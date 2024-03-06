from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "No such name found"
        except IndexError:
            return "Not found"
        except Exception as e:
            return f'Error: {e}'

    return inner


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        pattern = r'^\d{10}$'
        if not re.match(pattern, value):
            return "Invalid phone number format. The phone number must contain 10 digits"
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d-%m-%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        self.phones = [num for num in self.phones if num.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for num in self.phones:
            if num.value == old_phone:
                num.value = new_phone

    def find_phone(self, phone):
        return [str(num) for num in self.phones if num.value == phone]

    def __str__(self):
        return f"Contact name: {self.name.value} phones: {'; '.join(num.value for num in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        date_now = datetime.today().date()
        bday = []
        for record in self:
            if self[record].birthday:
                birthday = datetime.strptime(
                    str(self[record].birthday), "%d.%m.%Y").date()
                birthday = birthday.replace(year=date_now.year)
                days = (birthday - date_now).days
                if days <= 7:
                    if birthday.weekday() == 5:
                        birthday += timedelta(days=2)
                    elif birthday.weekday() == 6:
                        birthday += timedelta(days=1)
                    bday.append({'name': self[record].name.value, 'birthday': datetime.strftime(
                        birthday, "%d.%m.%Y")})
        return bday


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        return record.add_birthday(birthday)
    else:
        return "Contact not found"


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return record.birthday.value.strftime("%d.%m.%Y")
    return "Not found"


def birthdays(book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        result = ""
        for birthday_info in upcoming_birthdays:
            result += f"{birthday_info['name']}'s birthday is on {birthday_info['birthday']}.\n"
        return result.strip()
    else:
        return 'Not upcoming birthdays'


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book[name] = record
    return "Contact added."


@input_error
def change_contact(args, book):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book[name] = record
    return "Contact updated."


@input_error
def show_phone(args, book):
    name = args[0]
    phone = book[name]
    return phone


@input_error
def show_all(book):
    for k, v in book.items():
        print(f"{k}: {v}")


@input_error
def add_birthday(args, book):
    name, birthday = args
    book.find(name).birthday = birthday
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    return book.get(name)


def birthdays(book):
    return book.get_upcoming_birthdays()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == 'change':
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            show_all(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == '__main__':
    main()
