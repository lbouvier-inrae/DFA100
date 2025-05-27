from PyQt5.QtWidgets import QApplication
import sys

from controller.controller import VideoAnalyzerController
from view.view import VideoAnalyzerUI

def main():
    app = QApplication(sys.argv)
    view = VideoAnalyzerUI()
    controller = VideoAnalyzerController(view)
    view.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
