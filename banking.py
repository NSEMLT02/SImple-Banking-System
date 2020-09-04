from random import randrange
from math import ceil
import sqlite3


class EnesBanking(object):
    def __init__(self):
        # Setting up db connection
        self.conn = sqlite3.connect("card.s3db")
        self.cur = self.conn.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS card ( '
                         'id INTEGER,'
                         'number TEXT,'
                         'pin TEXT,'
                         'balance INTEGER DEFAULT 0 )')
        self.conn.commit()
        self.logged_card = None

    def principal_menu(self):
        # Principal Action menu
        print()
        valid = ("1", "2", "0")
        action = input("1. Create an account\n2. Log into account\n0. Exit\n")

        if action not in valid:
            print('Error, option not valid')
            self.principal_menu()
        if action == "0":
            print("Bye!")
            exit()
        elif action == "1":
            self.create_account()
        elif action == "2":
            self.login()

    def logged_in_menu(self):
        # Prompt action menu for logged in users
        print()
        valid = (1, 2, 3, 4, 5, 0)
        action = int(input("1. Balance\n2. Add income\n3. Do transfer"
                           "\n4. Close Account\n5. Log out\n0. Exit\n"))
        if action not in valid:
            print('Error, option not valid')
            self.logged_in_menu()
        if action == 0:
            print("Bye!")
            exit()
        elif action == 1:
            print(f"\nBalance: {self.balance(self.logged_card)}")
        elif action == 3:
            self.do_transfer()
        elif action == 2:
            self.add_income()
        elif action == 4:
            self.close_account()
        elif action == 5:
            self.logged_card = None
            print("You have successfully logged out!")
            self.principal_menu()

    def create_account(self):
        print()
        card_number, pin = map(str, self.create_credit_card_number())
        # Save information to db
        self.cur.execute("INSERT INTO card (pin, number) VALUES (?,?)", (pin, card_number))
        self.conn.commit()

        print("Your card has been created")
        print(f"Your card number:\n{card_number}\nYour card PIN:\n{pin}")
        self.principal_menu()

    def close_account(self):
        # Drop row form db with account information
        self.cur.execute("DELETE FROM card WHERE number=?", (self.logged_card,))
        self.conn.commit()
        print("The account has been closed!")
        self.logged_card = None
        self.principal_menu()

    def add_income(self):
        # Self explanatory
        income_to_add = int(input('Enter income:\n'))
        self.cur.execute('UPDATE card SET balance=balance+? WHERE number=? ', (income_to_add, self.logged_card))
        self.conn.commit()
        print('Income was added!')
        self.logged_in_menu()

    def do_transfer(self):
        # Self explanatory
        self.cur.execute('SELECT balance FROM card WHERE number=?', (self.logged_card,))
        usr_balance = self.cur.fetchone()[0]
        print('Transfer')

        transfer_to_card = input('Enter card number:\n')
        # Check for mistakes and exceptions in card number
        if transfer_to_card == self.logged_card:  # Check if user tries to transfer to itself
            print("You can't transfer money to the same account!")
            self.logged_in_menu()
        # Check if card passes luhn algorithm
        if str(EnesBanking.luhn_algorithm(transfer_to_card[:-1])) != transfer_to_card[-1]:
            print("Probably you made a mistake in the card number. Please try again!")
            self.logged_in_menu()
        transfer_to_card_inf = self.cur.execute('SELECT number FROM card WHERE number=?', (transfer_to_card,)) # Get info of transfer to card from db
        a = self.cur.fetchone()
        if not bool(a):
            print("Such a card does not exist")
            self.logged_in_menu()

        money_to_transfer = int(input('Enter how much money you want to transfer:\n'))
        if money_to_transfer > usr_balance:
            print("Not enough money!")
            self.logged_in_menu()
        # After error checking do the transfer
        self.cur.execute("UPDATE card SET balance=balance-? WHERE number=?", (money_to_transfer, self.logged_card))
        self.cur.execute("UPDATE card SET balance=balance+? WHERE number=?", (money_to_transfer, transfer_to_card))
        self.conn.commit()
        self.logged_in_menu()

    def login(self):
        # Login check and prompt
        print()
        number = input("Enter your card number:\n")
        pin = input("Enter your PIN:\n")
        self.cur.execute('SELECT number FROM card WHERE '
                         'number = ?'
                         'AND pin = ?', (number, pin))
        card = self.cur.fetchone()
        if card:
            self.logged_card = number
            print("\n You have successfully logged in!")
            self.logged_in_menu()
        else:
            print("\nWrong card number or PIN!")
            self.principal_menu()

    def balance(self, card_number):
        # Consult current balance of card
        self.cur.execute('SELECT balance FROM card WHERE number = ?', card_number)
        return self.cur.fetchone()

    @staticmethod
    def create_credit_card_number(iin='400000'):
        # Generate card and pin number
        bin_ = iin + str(randrange(0, 999999999)).zfill(9)
        pin = str(randrange(0, 9999)).zfill(4)
        card_number = bin_ + str(EnesBanking.luhn_algorithm(bin_))
        return card_number, pin

    @staticmethod
    def luhn_algorithm(bin_):
        # Luhn Algorithm, add checksum
        bin_ = [int(x) for x in bin_]
        bin_.reverse()

        doubles = bin_[::2]
        doubles = [i * 2 if (i * 2) < 9 else (i * 2) - 9 for i in doubles]
        final_sum = sum(doubles) + sum(bin_[1::2])
        return (final_sum * 9) % 10


if __name__ == '__main__':
    bank = EnesBanking()
    bank.principal_menu()
