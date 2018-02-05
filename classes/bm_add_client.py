
"""
    This file contains the definition for the Book Management Add Client Dialog class
"""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton


class BM_Add_Client_Dialog(QWidget):
    # define transaction signal
    transaction_finished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        # initialise UI and layout
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()

        # set window properties
        self.setMinimumSize(400, 200)
        self.setMaximumSize(1024, 200)

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
        _add_row("First Name", self.first_name)
        _add_row("Last Name", self.last_name)

        # interaction buttons
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setShortcut("Esc")
        btn_cancel.clicked.connect(self._cancel)

        self.btn_add = QPushButton("Add")
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
            "fname": self.first_name.text(),
            "lname": self.last_name.text(),
            "origin": self.origin,
            "purpose": self.purpose,
            "sid": self.sid
        })

        # close the window
        self.hide()

    def activate(self, purpose="add", values={}, sid=0):
        # reset everything
        if self.first_name and self.last_name:
            if len(values) == 0:
                self.first_name.setText("")
                self.last_name.setText("")
                self.origin = None
            else:
                self.first_name.setText(values["fname"])
                self.last_name.setText(values["lname"])
                self.origin = values["cid"]

        # update purpose
        self.purpose = purpose

        # update selected index
        self.sid = sid

        if self.purpose == "add":
            self.setWindowTitle("Add Client")
            self.btn_add.setText("Add")
        elif self.purpose == "edit":
            self.setWindowTitle('Editing client "%s %s"' % (values["fname"], values["lname"]))
            self.btn_add.setText("Update")

        # show this window
        self.show()
