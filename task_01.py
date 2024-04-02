from abc import ABC, abstractmethod
from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle


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
            self.value = datetime.strptime(value, '%d.%m.%Y')
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
        raise ValueError("Phone number not found")

    def find_phone(self, phone):
        return [str(num) for num in self.phones if num.value == phone]

    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError("Birthday exists")
        self.birthday = birthday

    def show_birthday(self, birthday):
        self.birthday = birthday
        if not self.birthday:
            raise ValueError("Birthday not found")
        return self.birthday.value.strftime("%d.%m.%Y")


class AddressBook(UserDict):
    def add_contact(self, args):
        name, phone = args
        self.data[name] = Record(name)
        self.data[name].add_phone(phone)

    def change_contact(self, args):
        name, new_phone = args
        record = self.data.get(name)
        if record:
            old_phone = record.phones[0].value
            record.delete_phone(old_phone)
            record.add_phone(new_phone)
            return "Contact updated."

    def show_phone(self, args):
        name = args[0]
        phone = self.data.get(name)
        if phone:
            return phone.phones[0].value

    def add_birthday(self, name, birthday):
        record = self.data.get(name)
        if record:
            record.add_birthday(birthday)
            return "Birthday recorded"
        else:
            return "Contact not found"

    def show_birthday(self, name):
        record = self.data.get(name)
        if record and record.birthday:
            return record.show_birthday()
        else:
            raise ValueError ("Not found")
        

    

    def birthdays(self):
        upcoming_birthdays = []
        today = datetime.combine(datetime.today(), datetime.min.time())
        for record in self.values():
            if record.birthday:
                if (record.birthday.value - today).days <= 7:
                    upcoming_birthdays.append(record.name.value)
        return '\n'.join(upcoming_birthdays) 



    def show_all(self):
        all_contacts = []
        for record in self.values():
            contact_info = f" Name: {record.name.value}"
            if record.phones:
                phone_info = ', '.join([phone.value for phone in record.phones])
                contact_info += f"  Phone: {phone_info}"
            if record.birthday:
                birthday_info = record.birthday.value.strftime("%d.%m.%Y")
                contact_info += f"  Birthday: {birthday_info}"
            all_contacts.append(contact_info)
        return '\n'.join(all_contacts)


class Bot(ABC):
    @abstractmethod
    def message(self):
        pass

    @abstractmethod
    def help(self):
        pass


class SimpleBot(Bot):
    def message(self, message):
        print(message)

    def help(self, message):
        print(message)


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def main():
    book = load_data()
    bot = SimpleBot()

    bot.message("Welcome to the assistant bot!")
    bot.help("Commands:\n"
             "add [name] [phone] - Create a new contact\n"
             "change [name] [new_phone] - Change phone number\n"
             "phone [name] - Show phone number\n"
             "all - Show all contacts\n"
             "add-birthday [name] [birthday] - Create birthday\n"
             "show-birthday [name] - Show birthday\n"
             "birthdays - Show upcoming birthdays")
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
            book.add_contact(args)
            bot.message("Contact added")
        elif command == 'change':
            bot.message(book.change_contact(args))

        elif command == "phone":
            bot.message(book.show_phone(args))
        elif command == "all":
            bot.message(book.show_all())
        elif command == "add-birthday":
            name, birthday = args
            bot.message(book.add_birthday(name, birthday))
        elif command == "show-birthday":
            name = args[0]
            bot.message(book.show_birthday(name))
        elif command == "birthdays":
            bot.message(book.birthdays)
        else:
            print("Invalid command.")


if __name__ == '__main__':
    main()
