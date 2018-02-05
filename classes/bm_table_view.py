"""
    This file contains the definition for the Book Management Table View class
"""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableView, QHeaderView
from classes.bm_table_model import BM_Table_Model, Model_Mode


class BM_Table_View(QTableView):
    contents_changed = pyqtSignal(int)

    def __init__(self):
        # initialise this as a subclass of QTableView
        super().__init__()

        # initialise our model
        self.model = BM_Table_Model()
        self.setModel(self.model)

        # keep track of the selected row
        self.selected_row = None
        self.activated.connect(self._update_selection)

        # set table view attributes
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def switch_mode(self, mode: Model_Mode):
        # nothing will be selected at this point
        self.selected_row = None

        # update mode
        self.model.mode = mode

        # update our model
        if mode == Model_Mode.Book:
            self.model.fetch("SELECT * FROM books")
        elif mode == Model_Mode.Client:
            self.model.fetch("SELECT * FROM clients")
        elif mode == Model_Mode.Log:
            self.model.fetch(
                "SELECT * FROM logs JOIN books ON logs.bid=books.bid JOIN clients ON logs.cid=clients.cid ORDER BY ldate DESC")

        self.model.layoutChanged.emit()

        # emit the "contents_changed" signal
        self.contents_changed.emit(len(self.model.items))

    def selected_item(self):
        # return the selected item
        return self.model.items[self.selected_row]

    def _update_selection(self, index):
        self.selected_row = index.row()
