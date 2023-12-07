import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMenu, QAction, \
    QDialog, QTableWidget, QTableWidgetItem, QLabel, QTabWidget, QTabBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QLineEdit

class BookmarksHistoryWindow(QDialog):
    def __init__(self, title):
        super().__init__()

        self.setWindowTitle(title)
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.items_label = QLabel(title)
        self.layout.addWidget(self.items_label)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(2)
        self.items_table.setHorizontalHeaderLabels(["Title", "URL"])
        self.layout.addWidget(self.items_table)

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Browser")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.nav_layout = QHBoxLayout()
        self.layout.addLayout(self.nav_layout)

        self.back_button = QPushButton("Back")
        self.nav_layout.addWidget(self.back_button)
        self.forward_button = QPushButton("Forward")
        self.nav_layout.addWidget(self.forward_button)
        self.reload_button = QPushButton("Reload")
        self.nav_layout.addWidget(self.reload_button)
        self.options_button = QPushButton("Options")
        self.nav_layout.addWidget(self.options_button)

        self.options_menu = QMenu(self)
        self.bookmarks_action = QAction("Bookmarks", self)
        self.history_action = QAction("History", self)
        self.bookmark_page_action = QAction("Bookmark Page", self)
        self.options_menu.addAction(self.bookmarks_action)
        self.options_menu.addAction(self.history_action)
        self.options_menu.addAction(self.bookmark_page_action)
        self.bookmarks_action.triggered.connect(self.show_bookmarks)
        self.history_action.triggered.connect(self.show_history)
        self.bookmark_page_action.triggered.connect(self.save_bookmark)
        self.options_button.setMenu(self.options_menu)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabBar().setContextMenuPolicy(3)
        self.tab_widget.tabBar().customContextMenuRequested.connect(self.tab_menu_requested)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.layout.addWidget(self.tab_widget)

        self.browser = QWebEngineView()
        self.tab_widget.addTab(self.browser, "New Tab")
        self.browser.page().loadFinished.connect(self.page_loaded)
        self.browser.page().titleChanged.connect(self.update_tab_title)

        self.load_page("https://www.google.com")

        self.bookmarks_window = None
        self.history_window = None
        self.history_pages = []
        self.back_button.clicked.connect(self.back_current_tab)
        self.forward_button.clicked.connect(self.forward_current_tab)
        self.reload_button.clicked.connect(self.reload_current_tab)

        self.url_bar = QLineEdit()  # Creating a QLineEdit for URL input
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_layout.addWidget(self.url_bar)

        # Connect the urlChanged signal to update_url_bar method
        self.browser.urlChanged.connect(self.update_url_bar)

    def back_current_tab(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.back()

    def forward_current_tab(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.forward()

    def reload_current_tab(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.reload()

    def load_page(self, url):
        qurl = QUrl(url)
        self.browser.setUrl(qurl)

    def show_bookmarks(self):
        if not self.bookmarks_window:
            self.bookmarks_window = BookmarksHistoryWindow("Bookmarks")
            self.bookmarks_window.items_table.cellDoubleClicked.connect(self.open_bookmark_in_tab)
        self.bookmarks_window.show()

    def show_history(self):
        if not self.history_window:
            self.history_window = BookmarksHistoryWindow("History")
            self.history_window.items_table.cellDoubleClicked.connect(self.open_history_in_tab)
            for title, url in self.history_pages:
                row_position = self.history_window.items_table.rowCount()
                self.history_window.items_table.insertRow(row_position)
                self.history_window.items_table.setItem(row_position, 0, QTableWidgetItem(title))
                self.history_window.items_table.setItem(row_position, 1, QTableWidgetItem(url))
        self.history_window.show()

    def save_bookmark(self):
        title = self.browser.page().title()
        url = self.browser.url().toString()
        if self.bookmarks_window:
            found = False
            for row in range(self.bookmarks_window.items_table.rowCount()):
                if self.bookmarks_window.items_table.item(row, 1).text() == url:
                    found = True
                    break
            if not found:
                row_position = self.bookmarks_window.items_table.rowCount()
                self.bookmarks_window.items_table.insertRow(row_position)
                self.bookmarks_window.items_table.setItem(row_position, 0, QTableWidgetItem(title))
                self.bookmarks_window.items_table.setItem(row_position, 1, QTableWidgetItem(url))

    def page_loaded(self):
        title = self.browser.page().title()
        url = self.browser.url().toString()

        # Add to history
        self.history_pages.append((title, url))

        index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.widget(index)
        current_index = self.tab_widget.indexOf(current_widget)
        self.tab_widget.setTabText(current_index, title)

    def update_tab_title(self, title):
        current_widget = self.tab_widget.currentWidget()
        index = self.tab_widget.indexOf(current_widget)
        if index != -1:
            self.tab_widget.setTabText(index, title)

    def open_bookmark_in_tab(self, row, col):
        url = self.bookmarks_window.items_table.item(row, 1).text()
        self.load_page(url)

    def open_history_in_tab(self, row, col):
        url = self.history_window.items_table.item(row, 1).text()
        self.load_page(url)

    def tab_menu_requested(self, pos):
        tab_bar = self.tab_widget.tabBar()
        index = tab_bar.tabAt(pos)
        if index < 0:
            return
        menu = QMenu()
        new_tab_action = QAction("New Tab", self)
        close_tab_action = QAction("Close Tab", self)
        menu.addAction(new_tab_action)
        menu.addAction(close_tab_action)
        new_tab_action.triggered.connect(self.open_new_tab)
        close_tab_action.triggered.connect(lambda: self.close_tab(index))
        menu.exec_(tab_bar.mapToGlobal(pos))

    def open_new_tab(self):
        new_browser = QWebEngineView()
        new_browser.setUrl(QUrl("https://www.google.com"))
        self.tab_widget.addTab(new_browser, "New Tab")
        self.tab_widget.setCurrentWidget(new_browser)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.load_page(url)

    def update_url_bar(self, q):
        self.url_bar.setText(q.toString())

    def load_page(self, url):
        qurl = QUrl(url)
        self.browser.setUrl(qurl)

def main():
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
