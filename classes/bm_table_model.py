"""
    This file contains the definition for the Book Management Table Model class
"""
from enum import Enum
from PyQt5.QtCore import Qt, QAbstractTableModel
from cs50 import SQL


class Model_Mode(Enum):
    # this enum defines the various model modes
    Book = 0
    Client = 1
    Log = 2


class BM_Table_Model(QAbstractTableModel):
    def __init__(self):
        # initialise this as a subclass of QAbstractTableModel
        super().__init__()

        # establish a connection to our database
        self.database = SQL("sqlite:///library.db")

        # model mode
        self.mode = Model_Mode.Book

        # keys per mode
        self._mbook = ["title", "stock"]
        self._mclient = ["fname", "lname"]
        self._mlog = ["title", "ltype", "fname", "lname", "ldate"]

        # header titles
        self._tbook = ["Title", "Stock"]
        self._tclient = ["First Name", "Last Name"]
        self._tlog = ["Title", "Type", "First Name", "Last Name", "Date"]

        # pre-initialise our items list
        self.items = []
        self.original = []
        self.searching = False

    def fetch(self, command):
        # clear our items list
        self.items = []

        # fetch new data from database
        rows = self.database.execute(command)

        # iteratively insert new data into our list
        for row in rows:
            self.items.append(row)

    def search(self, predicate):
        if predicate != "":
            # only clear our original list if the search flag is off
            if not self.searching:
                # store the original items in a temporary list
                self.original = []

            search_list = []

            # modify the target list depending on the search flag
            if self.searching:
                target_list = self.original
            else:
                target_list = self.items

            # selectively copy items to a temporary list
            for item in target_list:
                # item search scope
                item_scope = [
                    item.get("fname", "").lower(),
                    item.get("lname", "").lower(),
                    item.get("title", "").lower()
                ]

                # search the scope
                for s in item_scope:
                    if predicate.lower() in s:
                        search_list.append(item)
                        break

                if not self.searching:
                    self.original.append(item)

            # point to our new filtered list
            self.items = search_list

            # update the search flag
            self.searching = True
        else:
            if self.searching:
                # copy the original items back to the items list
                self.items = []

                for item in self.original:
                    self.items.append(item)

                # update search flag
                self.searching = False

        # update model
        self.layoutChanged.emit()

    # this method handles CUD operations for the "clients" table our database
    def client_mod(self, mod_type, first_name=None, last_name=None, target=None, sid=None):
        if mod_type == "add":
            # check if both arguments are not "None"
            if first_name and last_name:
                self.database.execute('INSERT INTO clients (fname, lname) VALUES (:fname, :lname)',
                                      fname=first_name, lname=last_name)

                # fetch this client's ID
                cid_r = self.database.execute("SELECT cid FROM clients WHERE fname=:fname AND lname=:lname LIMIT 1",
                                              fname=first_name, lname=last_name)

                # add the new client to the model
                self.items.append({
                    "cid": cid_r[0]["cid"],
                    "fname": first_name,
                    "lname": last_name
                })

        elif mod_type == "edit":
            if first_name and last_name and target and sid is not None:
                self.database.execute('UPDATE clients SET fname=:fname, lname=:lname WHERE cid=:target',
                                      target=target, fname=first_name, lname=last_name)

                self.items[sid] = ({
                    "cid": self.items[sid]["cid"],
                    "fname": first_name,
                    "lname": last_name
                })

        elif mod_type == "delete":
            if target and sid is not None:
                # delete the client in the database
                self.database.execute("DELETE FROM clients WHERE cid=:origin",
                                      origin=target)
                self.database.execute("DELETE FROM logs WHERE cid=:origin",
                                      origin=target)

                # delete the client from the model
                del self.items[sid]

        # update model
        self.layoutChanged.emit()

    # this method handles CUD operations for the "books" table in our database
    def book_mod(self, mod_type, title=None, stock=None, target=None, sid=None):
        # convert stock into an integer (if it's available)
        if stock:
            try:
                stock = int(stock)
            except:
                print("Debug: conversion error!")
                return

        # insert the new book to our database
        if mod_type == "add":
            if title and stock:
                self.database.execute('INSERT INTO books (title, stock) VALUES (:title, :stock)',
                                      title=title, stock=stock)

                # fetch this book's ID
                bid_r = self.database.execute("SELECT bid FROM books WHERE title=:title AND stock=:stock LIMIT 1",
                                              title=title, stock=stock)

                # add the new book to the model
                self.items.append({
                    "bid": bid_r[0]["bid"],
                    "title": title,
                    "stock": stock
                })

        elif mod_type == "edit":
            if title and stock and target and sid is not None:
                # update the database
                self.database.execute('UPDATE books SET title=:title, stock=:stock WHERE bid=:origin',
                                      title=title, stock=stock, origin=target)

                # update our book in the model
                self.items[sid] = {
                    "bid": self.items[sid]["bid"],
                    "title": title,
                    "stock": stock
                }

        elif mod_type == "delete":
            if target and sid is not None:
                # delete the book in the database
                self.database.execute("DELETE FROM books WHERE bid=:origin",
                                      origin=target)
                self.database.execute("DELETE FROM logs WHERE bid=:origin",
                                      origin=target)

                # delete the book from the model
                del self.items[sid]

        # update the model
        self.layoutChanged.emit()

    def transaction_mod(self, mod_type, bid, cid, ttype, lid=None, sid=None):
        if mod_type == "add":
            if bid and cid and ttype:
                # fetch book data
                book_data = self.database.execute("SELECT * FROM books WHERE bid=:bid", bid=bid)[0]

                if book_data["stock"] == 0 and ttype == "Borrowing":
                    print("Debug: out of stock!")
                else:
                    # insert this transaction to the database
                    self.database.execute(
                        "INSERT INTO logs (bid, cid, ltype, ldate) VALUES (:bid, :cid, :ltype, DATETIME('now'))",
                        bid=bid, cid=cid, ltype=ttype)

                    # update book stock
                    delta = -1 if ttype == "Borrowing" else 1
                    self.database.execute("UPDATE books SET stock=:stock WHERE bid=:bid",
                                          stock=book_data["stock"] + delta, bid=bid)

        elif mod_type == "delete":
            if lid and sid is not None:
                # delete this transaction from the database
                self.database.execute("DELETE FROM logs WHERE lid=:lid", lid=lid)

                # delete this transaction from the model
                del self.items[sid]

        # update the model
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        if self.mode == Model_Mode.Book:
            return len(self._mbook)
        elif self.mode == Model_Mode.Client:
            return len(self._mclient)
        elif self.mode == Model_Mode.Log:
            return len(self._mlog)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if self.mode == Model_Mode.Book:
                return self.items[index.row()][self._mbook[index.column()]]
            elif self.mode == Model_Mode.Client:
                return self.items[index.row()][self._mclient[index.column()]]
            elif self.mode == Model_Mode.Log:
                return self.items[index.row()][self._mlog[index.column()]]

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if self.mode == Model_Mode.Book:
                return self._tbook[section]
            elif self.mode == Model_Mode.Client:
                return self._tclient[section]
            elif self.mode == Model_Mode.Log:
                return self._tlog[section]
