
"""
    This file contains the definition for the Book Management Add Book Dialog class
"""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QSpinBox


class BM_Add_Book_Dialog(QWidget):
    # define transaction signal
    transaction_finished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        # initialise UI and layout
        self.btitle = QLineEdit()
        self.stock = QSpinBox()

        self.stock.setMinimum(0)
        self.stock.setMaximum(10000)

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
        _add_row("Book Title", self.btitle)
        _add_row("Stock", self.stock)

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
            "title": self.btitle.text(),
            "purpose": self.purpose,
            "origin": self.origin,
            "sid": self.sid,
            "stock": self.stock.value()
        })

        # close the window
        self.hide()

    def activate(self, purpose="add", values={}, sid=0):
        # reset everything
        if self.btitle and self.stock:
            if len(values) == 0:
                self.btitle.setText("")
                self.stock.setValue(0)
                self.origin = None
            else:
                # try to convert "stock"'s type to integer
                try:
                    values["stock"] = int(values["stock"])
                except:
                    # default to zero, if we fail type conversion
                    print("Debug: type conversion error [location: bm_add_book activation]")
                    values["stock"] = 0

                self.btitle.setText(values["title"])
                self.stock.setValue(values["stock"])
                self.origin = values["bid"]

        # update our dialog purpose
        self.purpose = purpose
        self.sid = sid

        # update window title and ok button text
        if purpose == "add":
            self.setWindowTitle("Add Book")
            self.btn_add.setText("Add")
        elif purpose == "edit":
            self.setWindowTitle('Editing book "%s"' % values["title"])
            self.btn_add.setText("Update")

        # show this window
        self.show()
