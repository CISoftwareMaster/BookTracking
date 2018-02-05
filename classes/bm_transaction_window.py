
"""
    This file contains the definition for the Book Management Transaction class
"""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox


class BM_Transaction_Dialog(QWidget):
    # define transaction signal
    transaction_finished = pyqtSignal(dict)

    def __init__(self, db):
        super().__init__()

        # initialise UI and layout
        self.book = QComboBox()
        self.client = QComboBox()
        self.ttype = QComboBox()

        # initialise database connection
        self.database = db

        # transaction types
        self.ttypes = ["Borrowing", "Returning"]

        for t in self.ttypes:
            self.ttype.addItem(t)

        self.setWindowTitle("Record Transaction")

        # set window properties
        self.setMinimumSize(400, 230)
        self.setMaximumSize(1024, 230)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # add a row with label
        def _add_row(label, widget):
            row = QWidget()

            # initialise layout
            rlayout = QHBoxLayout()
            rlayout.addWidget(QLabel(label))
            rlayout.addWidget(widget)

            row.setLayout(rlayout)
            layout.addWidget(row)

        # insert rows to our layout
        _add_row("Book", self.book)
        _add_row("Client", self.client)
        _add_row("Transaction Type", self.ttype)

        # interaction buttons
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setShortcut("Esc")
        btn_cancel.clicked.connect(self._cancel)

        self.btn_add = QPushButton("Record Transaction")
        self.btn_add.setShortcut("Return")
        self.btn_add.clicked.connect(self._done)

        # insert buttons to layout
        layout.addWidget(self.btn_add)
        layout.addWidget(btn_cancel)

        self.setLayout(layout)

    def _cancel(self):
        # close this widget window
        self.hide()

    def _done(self):
        # send the "transaction_finished" signal
        self.transaction_finished.emit({
            "bid": self.books[self.book.currentIndex()]["bid"],
            "stock": self.books[self.book.currentIndex()]["stock"],
            "cid": self.clients[self.client.currentIndex()]["cid"],
            "type": self.ttypes[self.ttype.currentIndex()]
        })

        # close the window
        self.hide()

    def activate(self, psb=None, psc=None):
        # show this window
        self.show()

        # fetch books and clients
        self.books = self.database.execute("SELECT * FROM books")
        self.clients = self.database.execute("SELECT * FROM clients")

        # cancel activation if we have no data on either columns
        if len(self.books) == 0 or len(self.clients) == 0:
            QMessageBox.warning(self, "No data!",
                                "To record a transaction you must have at least one book and one client in the database.")
            self.hide()

        # clear our combo box inputs
        self.book.clear()
        self.client.clear()

        # populate our combo box inputs
        for book in self.books:
            self.book.addItem(book["title"])

        for client in self.clients:
            self.client.addItem("%s %s" % (client["fname"], client["lname"]))

        # use the pre-selected values (if they are available)
        if psb:
            self.book.setCurrentText(psb)

        if psc:
            self.client.setCurrentText(psc)
