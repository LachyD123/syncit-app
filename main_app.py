# main_app.py
import sys
import os

# Ensure the project root is in PYTHONPATH if running main_app.py directly from root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication
from gui.ram_api_gui import RamApiGuiPyQt

def main():
    app_argv = sys.argv if hasattr(sys, 'argv') else []
    app = QApplication(app_argv)
    main_window = RamApiGuiPyQt()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
