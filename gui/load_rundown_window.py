# gui/load_rundown_window.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
)
from PyQt6.QtCore import Qt

# For type hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from data_model.structure_model import StructureModel
    from core_logic.cpt_manager import CPTManager
    from core_logic.project_manager import ProjectManager

class LoadRundownWindow(QDialog):
    # Signals for future threading will be added here
    # e.g., progress_updated = pyqtSignal(int, str)
    # e.g., process_finished = pyqtSignal(bool, str)

    def __init__(self, structure_model: 'StructureModel', cpt_manager: 'CPTManager', project_manager: 'ProjectManager', parent=None):
        super().__init__(parent)
        self.structure_model = structure_model
        self.cpt_manager = cpt_manager
        self.project_manager = project_manager

        self.setWindowTitle("Load Rundown Process")
        self.setMinimumSize(600, 400)
        self.setModal(False) # Allow interaction with main window

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Rundown")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.close_button = QPushButton("Close") # Added close button

        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.close_button)
        layout.addLayout(controls_layout)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        # Status
        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        # Connect button signals
        self.start_button.clicked.connect(self._start_process)
        self.pause_button.clicked.connect(self._pause_process)
        self.stop_button.clicked.connect(self._stop_process)
        self.close_button.clicked.connect(self.accept) # QDialog's accept() closes it

        self.log_message("Load Rundown window initialized.", "INFO")

    def log_message(self, message: str, level: str = "INFO"):
        self.log_display.append(f"[{level}] {message}")

    def _start_process(self):
        self.log_message("Start button clicked.", "DEBUG")
        self.status_label.setText("Status: Starting...")
        # Placeholder: Actual logic will involve starting a QThread
        # For now, simulate some activity
        self.log_message("Load rundown process initiated (placeholder).", "INFO")
        self.log_message(f"Accessing StructureModel: {self.structure_model.gui_data.root_directory if self.structure_model else 'N/A'}", "DEBUG")
        self.log_message(f"CPT Manager instance: {'Available' if self.cpt_manager else 'N/A'}", "DEBUG")
        self.log_message(f"Project Manager instance: {'Available' if self.project_manager else 'N/A'}", "DEBUG")

        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)

    def _pause_process(self):
        self.log_message("Pause button clicked.", "DEBUG")
        if self.pause_button.text() == "Pause":
            self.status_label.setText("Status: Paused")
            self.pause_button.setText("Resume")
            # Placeholder: Actual logic to pause the thread
        else:
            self.status_label.setText("Status: Resuming...")
            self.pause_button.setText("Pause")
            # Placeholder: Actual logic to resume the thread

    def _stop_process(self):
        self.log_message("Stop button clicked.", "DEBUG")
        self.status_label.setText("Status: Stopping...")
        # Placeholder: Actual logic to stop the thread
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("Pause")
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Stopped/Idle")

    def closeEvent(self, event):
        # This method is called when the dialog is closed (e.g., by 'X' button or self.accept()/self.reject())
        if self.stop_button.isEnabled(): # If process might be running
            self._stop_process() # Attempt to stop gracefully
        self.log_message("Load Rundown window closed.", "INFO")
        super().closeEvent(event)


# Minimal test execution
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    class MockObj: pass
    app = QApplication(sys.argv)
    dialog = LoadRundownWindow(MockObj(), MockObj(), MockObj())
    dialog.show()
    sys.exit(app.exec())