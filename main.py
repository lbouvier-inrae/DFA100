from PyQt5.QtWidgets import QApplication
from interface.ui import VideoAnalyzerUI
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoAnalyzerUI()
    window.show()
    sys.exit(app.exec())