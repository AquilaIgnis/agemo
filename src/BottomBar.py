# pyright: reportOptionalMemberAccess=none
#
#  https://github.com/acidburnmonkey


import subprocess
import time

import PyQt6.QtWidgets as qt
from PyQt6.QtCore import Qt

from constants import get_host_env, get_logger
from HyprParser import HyprpaperWrite
from SharedData import SharedData

logger = get_logger(__name__)


# bottom bar
class BottomBar(qt.QWidget):
    def __init__(self, shared_data: SharedData, parent: qt.QWidget | None = None):
        super().__init__(parent)

        self.monitors: list[str] = shared_data.data["monitors"]
        self.shared_data: SharedData = shared_data

        # buttons
        self.applyButton = qt.QPushButton("Apply")
        self.applyButton.clicked.connect(self.apply)
        self.monitors_select = qt.QComboBox()
        self.monitors_select.addItems(self.monitors)
        self.current_monitor: str = self.monitors[0]

        # events
        self.monitors_select.currentTextChanged.connect(self.select_monitor)

        # Layout and  frame
        self.bframe = qt.QFrame(self)
        self.b_layout = qt.QHBoxLayout(self.bframe)
        self.b_layout.addWidget(self.applyButton)
        self.b_layout.addWidget(self.monitors_select)

        # mainLayout
        self.main_layout = qt.QHBoxLayout(self)
        self.main_layout.addWidget(self.bframe)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Styling
        self.initUi()

    def initUi(self):
        self.b_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.b_layout.setSpacing(4)

        self.bframe.setStyleSheet(
            "QFrame{border:1px solid #cad3f5; border-radius: 10px;}"
        )

        self.applyButton.setFixedSize(80, 20)  # W , H
        self.monitors_select.setFixedSize(100, 20)  # W , H
        self.monitors_select.setObjectName("monitors_select")

    def select_monitor(self, selected: str):
        self.current_monitor = selected
        logger.info(f"selected > self.current_monitor: {self.current_monitor}")

    def apply(self):
        writer = HyprpaperWrite()

        if self.shared_data.selectedImage:
            logger.info(f"applying to : {self.current_monitor}")
            logger.info(f"Image selected : {self.shared_data.selectedImage}")

            try:
                writer.hypr_write(self.shared_data.selectedImage, self.current_monitor)
                subprocess.call(["kill", "hyprpaper"], env=get_host_env())
                time.sleep(1)
                subprocess.Popen(["hyprpaper"], env=get_host_env())
            except FileNotFoundError:
                logger.error("⛔ Hyprpaper is not installed")
