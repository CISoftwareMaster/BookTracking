"""
    This file contains the definition for the Book Management Main Window class
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, qApp, QAction, QMessageBox, QLineEdit, QVBoxLayout, QWidget
from classes.bm_table_model import Model_Mode
from classes.bm_table_view import BM_Table_View
from classes.bm_add_book import BM_Add_Book_Dialog
from classes.bm_add_client import BM_Add_Client_Dialog
from classes.bm_transaction_window import BM_Transaction_Dialog


class BM_Main_Window(QMainWindow):
    def __init__(self):
        # initialise this as a subclass of QMainWindow
        super().__init__()

        # initialise view
        self.view = QWidget()

        # initialise our search bar component
        self.searchbar = QLineEdit()
        self.searchbar.setPlaceholderText("Search")

        # initialise our table view component
        self.table_view = BM_Table_View()
        self.table_view.switch_mode(Model_Mode.Book)
        self.table_view.contents_changed.connect(self._table_view_updated)

        # initialise our dialog classes
        self._add_book_dialog = BM_Add_Book_Dialog()
        self._add_client_dialog = BM_Add_Client_Dialog()
        self._transaction_dialog = BM_Transaction_Dialog(self.table_view.model.database)

        # point to our transaction callback functions
        self._add_book_dialog.transaction_finished.connect(self._add_book_finished)
        self._add_client_dialog.transaction_finished.connect(self._add_client_finished)
        self._transaction_dialog.transaction_finished.connect(self._transaction_finished)

        # handle search
        self.searchbar.textEdited.connect(self._search_items)

        self.setCentralWidget(self.view)

        # set up user interface
        self.init_ui()

    def init_ui(self):
        # set up layout
        layout = QVBoxLayout()

        layout.addWidget(self.searchbar)
        layout.addWidget(self.table_view)

        self.view.setLayout(layout)

        # setup window geometry
        self.setMinimumSize(480, 340)

        # set window title
        self.setWindowTitle("Book Management - Books")

        # setup our menu and status bars
        self.menubar = self.menuBar()
        self.statusBar().showMessage("Welcome to the Book Management interface!")

        # create our menus
        self.init_menu()

    def init_menu(self):
        m_app = self.menubar.addMenu("&Book Management")

        # set up "Book Management" actions
        a_app_add_book = QAction("Add &Book", self)
        a_app_add_book.setShortcut("Ctrl+1")
        a_app_add_book.setStatusTip("Insert a book entry to the database.")
        a_app_add_book.triggered.connect(self._add_book)
        m_app.addAction(a_app_add_book)

        a_app_add_client = QAction("Add &Client", self)
        a_app_add_client.setShortcut("Ctrl+2")
        a_app_add_client.setStatusTip("Insert a client entry to the database.")
        a_app_add_client.triggered.connect(self._add_client)
        m_app.addAction(a_app_add_client)

        a_app_record_transaction = QAction("Record &Transaction", self)
        a_app_record_transaction.setShortcut("Ctrl+3")
        a_app_record_transaction.setStatusTip("Record a transaction to the database.")
        a_app_record_transaction.triggered.connect(self._record_transaction)
        m_app.addAction(a_app_record_transaction)

        a_app_refresh = QAction("&Refresh", self)
        a_app_refresh.setShortcut("Ctrl+R")
        a_app_refresh.setStatusTip("Refresh the active table.")
        a_app_refresh.triggered.connect(self._refresh)
        m_app.addAction(a_app_refresh)

        m_app.addSeparator()

        a_app_quit = QAction("&Quit", self)
        a_app_quit.setShortcut("Ctrl+Q")
        a_app_quit.setStatusTip("Exit this application...")
        a_app_quit.triggered.connect(qApp.quit)
        m_app.addAction(a_app_quit)

        m_view = self.menubar.addMenu("&View")

        # set up "View" actions
        a_view_books = QAction("&Books View", self)
        a_view_books.setShortcut("Ctrl+Shift+1")
        a_view_books.setStatusTip("Switch to books view.")
        a_view_books.triggered.connect(self._switch_to_books)
        m_view.addAction(a_view_books)

        a_view_client = QAction("&Clients View", self)
        a_view_client.setShortcut("Ctrl+Shift+2")
        a_view_client.setStatusTip("Switch to clients view.")
        a_view_client.triggered.connect(self._switch_to_clients)
        m_view.addAction(a_view_client)

        a_view_logs = QAction("&Logs View", self)
        a_view_logs.setShortcut("Ctrl+Shift+3")
        a_view_logs.setStatusTip("Switch to logs view.")
        a_view_logs.triggered.connect(self._switch_to_logs)
        m_view.addAction(a_view_logs)

        # books action menu
        self.m_books = self.menubar.addMenu("B&ooks")
        self.a_books_edit = QAction("&Edit book", self)
        self.a_books_edit.setShortcut("Return")
        self.a_books_edit.setStatusTip("Edit the currently selected book.")
        self.a_books_edit.triggered.connect(self._edit_book)
        self.m_books.addAction(self.a_books_edit)

        self.a_books_delete = QAction("&Delete book", self)
        self.a_books_delete.setShortcut("Delete")
        self.a_books_delete.setStatusTip("Delete the currently selected book.")
        self.a_books_delete.triggered.connect(self._delete_book)
        self.m_books.addAction(self.a_books_delete)

        # clients action menu
        self.m_clients = self.menubar.addMenu("&Clients")
        self.a_clients_edit = QAction("&Edit client", self)
        self.a_clients_edit.setStatusTip("Edit the currently selected client.")
        self.a_clients_edit.triggered.connect(self._edit_client)
        self.m_clients.addAction(self.a_clients_edit)

        self.a_clients_delete = QAction("&Delete client", self)
        self.a_clients_delete.setStatusTip("Delete the currently selected client.")
        self.a_clients_delete.triggered.connect(self._delete_client)
        self.m_clients.addAction(self.a_clients_delete)

        # initially disable the clients menu
        self.m_clients.setEnabled(False)

        # help menu
        m_help = self.menubar.addMenu("&Help")
        a_help_about = QAction("About &Book Manager", self)
        a_help_about.setShortcut("F1")
        a_help_about.setStatusTip("Show information about Book Manager.")
        a_help_about.triggered.connect(self._about_app)
        m_help.addAction(a_help_about)

        a_help_qt = QAction("About &Qt", self)
        a_help_qt.setStatusTip("Show information about Qt.")
        a_help_qt.triggered.connect(self._about_qt)
        m_help.addAction(a_help_qt)

    def _search_items(self, predicate):
        # pass the predicate to our model
        self.table_view.model.search(predicate)

        # update status bar
        if predicate != "":
            self.statusBar().showMessage('Showing results for "%s"' % predicate)
        else:
            self.statusBar().showMessage("Search finished...")

    # confirmation dialog
    def confirm(self, title, message):
        response = QMessageBox.question(self, title, message)

        # return the response
        return (response == QMessageBox.Yes)

    # help callback functions
    def _about_app(self):
        # show app information
        QMessageBox.information(self, "About the Book Management Interface",
                                "Book Management Interface\n"
                                "version 1.0.0.0\n\n"
                                "Developed by Charles Mozar\n"
                                "Copyright (C) CSEM 2018")

    def _about_qt(self):
        # show Qt information
        QMessageBox.aboutQt(self)

    # table view update callback function
    @pyqtSlot(int)
    def _table_view_updated(self, x):
        self.statusBar().showMessage("Loaded %i item(s)..." % x)

    # mode switching methods
    def _switch_to_books(self):
        # switch to books mode
        self.table_view.switch_mode(Model_Mode.Book)

        # enable the books menu
        self.m_books.setEnabled(True)
        self.a_books_delete.setEnabled(True)

        # disable the clients menu
        self.m_clients.setEnabled(False)

        # update keyboard shortcuts
        self.a_books_delete.setShortcut("Delete")
        self.a_books_edit.setShortcut("Return")
        self.a_clients_edit.setShortcut("")
        self.a_clients_delete.setShortcut("")

        # reset search bar
        self.searchbar.setText("")

        # update window title
        self.setWindowTitle("Book Management - Books")

    def _switch_to_clients(self):
        # switch to clients mode
        self.table_view.switch_mode(Model_Mode.Client)

        # enable the clients menu
        self.m_clients.setEnabled(True)
        self.a_clients_delete.setEnabled(True)

        # disable the books menu
        self.m_books.setEnabled(False)
        self.a_books_delete.setEnabled(False)

        # update keyboard shortcuts
        self.a_clients_edit.setShortcut("Return")
        self.a_clients_delete.setShortcut("Delete")
        self.a_books_edit.setShortcut("")
        self.a_books_delete.setShortcut("")

        # reset search bar
        self.searchbar.setText("")

        self.setWindowTitle("Book Management - Clients")

    def _switch_to_logs(self):
        # switch to logs mode
        self.table_view.switch_mode(Model_Mode.Log)
        self.m_books.setEnabled(True)
        self.a_books_delete.setEnabled(False)
        self.m_clients.setEnabled(True)
        self.a_clients_delete.setEnabled(False)

        # update keyboard shortcuts
        self.a_clients_delete.setShortcut("Delete")
        self.a_books_delete.setShortcut("Delete")
        self.a_clients_edit.setShortcut("Shift+C")
        self.a_books_edit.setShortcut("Shift+B")

        # reset search bar
        self.searchbar.setText("")

        self.setWindowTitle("Book Management - Logs")

    def _refresh(self):
        # reset search bar
        self.searchbar.setText("")

        self.table_view.switch_mode(self.table_view.model.mode)

    # add items methods
    def _add_book(self):
        # show the add book dialog
        self._add_book_dialog.activate(purpose="add")

        # switch to book view
        self._switch_to_books()

        # adjust its positioning
        self._add_book_dialog.move(self.x(), self.y())

    def _add_client(self):
        # show the add client dialog
        self._add_client_dialog.activate()

        # adjust its positioning
        self._add_client_dialog.move(self.x(), self.y())

        # switch to clients view
        self._switch_to_clients()

    def _record_transaction(self):
        # pre-selection values
        psb = None
        psc = None

        # if the user selects a book or a client, update the index
        if self.table_view.selected_row is not None:
            # get selection
            selection = self.table_view.selected_item()

            if self.table_view.model.mode == Model_Mode.Book:
                psb = selection["title"]
                self.statusBar().showMessage('Selecting "%s" for book...' % psb)
            elif self.table_view.model.mode == Model_Mode.Client:
                psc = "%s %s" % (selection["fname"], selection["lname"])
                self.statusBar().showMessage('Selecting "%s" for client...' % psc)

        # adjust its positioning
        self._transaction_dialog.move(self.x(), self.y())

        # activate the transaction dialog
        self._transaction_dialog.activate(psb, psc)

    # book menu methods
    def _edit_book(self):
        if self.table_view.selected_row:
            # get the selected item
            selection = self.table_view.selected_item()

            # adjust positioning
            self._add_book_dialog.move(self.x(), self.y())

            # open the add book dialog in edit mode
            self._add_book_dialog.activate(
                purpose="edit", values=selection, sid=self.table_view.selected_row)

    def _delete_book(self):
        # get the selected item
        selection = self.table_view.selected_item()

        # verify this action first
        if self.confirm("Are you sure?", 'Deleting "%s" is irreversible!' % selection["title"]):
            if self.table_view.selected_row:
                # exterminate this book!
                self.table_view.model.book_mod(
                    "delete", target=selection["bid"], sid=self.table_view.selected_row)

                # update status bar
                self.statusBar().showMessage(
                    'Deleting "%s" from the database...' % selection["title"])

    # client menu methods
    def _edit_client(self):
        # get the selected item
        if self.table_view.selected_row:
            selection = self.table_view.selected_item()

            # adjust positioning
            self._add_client_dialog.move(self.x(), self.y())

            # activate the client dialog in edit mode
            self._add_client_dialog.activate(
                purpose="edit", values=selection, sid=self.table_view.selected_row)

    def _delete_client(self):
        # get the selected item
        selection = self.table_view.selected_item()

        # verify this action first
        if self.confirm("Are you sure?", 'Deleting "%s %s" is irreversible!' %
                        (selection["fname"], selection["lname"])):
            if self.table_view.selected_row:
                # delete this book
                self.table_view.model.client_mod(
                    "delete", target=selection["cid"], sid=self.table_view.selected_row)

                # update status bar
                self.statusBar().showMessage('Deleting "%s %s" from the database...' %
                                             (selection["fname"], selection["lname"]))

    # define our transaction callback functions
    @pyqtSlot(dict)
    def _add_book_finished(self, response):
        if response["title"] and response["stock"] and response["purpose"]:
            if response["purpose"] == "add":
                self.table_view.model.book_mod(
                    "add", response["title"], response["stock"])

            elif response["purpose"] == "edit" and response["origin"]:
                self.table_view.model.book_mod(
                    "edit", response["title"], response["stock"], response["origin"], response["sid"])

            # switch to book view
            self._switch_to_books()

    @pyqtSlot(dict)
    def _add_client_finished(self, response):
        if response["fname"] and response["lname"] and response["purpose"]:
            if response["purpose"] == "add":
                self.table_view.model.client_mod(
                    "add", response["fname"], response["lname"])

            elif response["purpose"] == "edit" and response["origin"]:
                self.table_view.model.client_mod(
                    "edit", response["fname"], response["lname"], response["origin"], response["sid"])

            # switch to book view
            self._switch_to_clients()

    @pyqtSlot(dict)
    def _transaction_finished(self, response):
        if response["bid"] and response["cid"] and response["type"] and response["stock"] is not None:
            # handle "out of stock" event
            if response["type"] == "Borrowing" and response["stock"] == 0:
                QMessageBox.warning(self, "Invalid Transaction", "This book is out of stock!")
            else:
                # insert this transaction to the database
                self.table_view.model.transaction_mod(
                    "add", response["bid"], response["cid"], response["type"])

                # switch to logs view
                self._switch_to_logs()
