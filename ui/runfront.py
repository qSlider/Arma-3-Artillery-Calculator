import sys
from PyQt5 import QtWidgets
from ui.mainwindow import MainWindow  # Импортируйте MainWindow

app = QtWidgets.QApplication(sys.argv)

# Инициализируйте MainWindow напрямую
window = MainWindow()
window.show()

sys.exit(app.exec_())
