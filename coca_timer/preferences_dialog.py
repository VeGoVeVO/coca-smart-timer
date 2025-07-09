"""
Modern preferences dialog for COCA Smart Timer.
Matches the exact theme and styling of the trigger word dialog.
"""

import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QRadioButton, QButtonGroup, QWidget, QSizePolicy, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QPainter, QColor, QPen


class ToggleSwitch(QWidget):
    """Custom toggle switch widget."""
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(45, 22)  # Smaller size
        self.setCheckable(True)
        self._checked = False
        self._circle_position = 2

        # Animation for smooth toggle
        self.animation = QPropertyAnimation(self, b"circle_position")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.setDuration(200)

    def setCheckable(self, checkable):
        pass

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self.move_circle()
            self.toggled.emit(checked)

    def move_circle(self):
        if self._checked:
            end_position = self.width() - 20  # Adjusted for smaller circle
        else:
            end_position = 2

        self.animation.setStartValue(self._circle_position)
        self.animation.setEndValue(end_position)
        self.animation.start()

    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, position):
        self._circle_position = position
        self.update()

    circle_position = pyqtProperty(int, get_circle_position, set_circle_position)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background track
        if self._checked:
            track_color = QColor(107, 155, 115)  # Green when on
        else:
            track_color = QColor(74, 124, 89)    # Darker green when off

        painter.setBrush(track_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 11, 11)  # Smaller radius

        # Draw circle
        circle_color = QColor(232, 245, 232)  # Light color for circle
        painter.setBrush(circle_color)
        painter.drawEllipse(self._circle_position, 2, 18, 18)  # Smaller circle


class PreferencesDialog(QDialog):
    """Modern preferences dialog matching the trigger word dialog theme."""

    # Signal emitted when preferences are saved
    preferences_saved = pyqtSignal(dict)

    def __init__(self, parent=None, current_settings=None):
        """
        Initialize modern preferences dialog.

        Args:
            parent: Parent widget
            current_settings: Dict with current crop and planter settings
        """
        super().__init__(parent)
        self.current_settings = current_settings or {
            'crop_type': 'coca',
            'planter_type': 'basic',
            'auto_detect_crop': True  # Default to auto-detection enabled
        }

        self.setWindowTitle("Growing Preferences")
        self.setFixedSize(480, 520)  # Smaller size without time info box
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setup_ui()
        self.setup_styling()
        self.center_on_screen()
        self.load_current_settings()

    def setup_ui(self):
        """Setup the modern UI components with proper spacing and layout."""
        # Main layout with no margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main container
        self.container = QWidget()
        self.container.setObjectName("container")

        # Container layout with proper margins
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(0)  # We'll add manual spacing

        # Title
        self.title_label = QLabel("Growing Preferences")
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFixedHeight(40)
        container_layout.addWidget(self.title_label)
        container_layout.addSpacing(20)

        # Auto-Detection Section
        auto_detect_label = QLabel("Detection Mode")
        auto_detect_label.setObjectName("section_title")
        auto_detect_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        auto_detect_label.setFixedHeight(30)
        container_layout.addWidget(auto_detect_label)
        container_layout.addSpacing(10)

        # Auto-detection toggle switch with label
        auto_detect_container = QWidget()
        auto_detect_layout = QHBoxLayout(auto_detect_container)
        auto_detect_layout.setContentsMargins(10, 5, 10, 5)
        auto_detect_layout.setSpacing(15)

        # Toggle switch
        self.auto_detect_toggle = ToggleSwitch()
        self.auto_detect_toggle.setChecked(True)  # Default enabled
        self.auto_detect_toggle.toggled.connect(self.on_auto_detect_toggled)
        auto_detect_layout.addWidget(self.auto_detect_toggle)

        # Label with proper sizing
        auto_detect_label = QLabel("Auto Crop Type Detection")
        auto_detect_label.setObjectName("toggle_label")
        auto_detect_label.setMinimumHeight(30)
        auto_detect_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        auto_detect_layout.addWidget(auto_detect_label)

        container_layout.addWidget(auto_detect_container)
        container_layout.addSpacing(25)

        # Crop Type Section
        crop_label = QLabel("Manual Crop Selection")
        crop_label.setObjectName("section_title")
        crop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        crop_label.setFixedHeight(30)
        container_layout.addWidget(crop_label)
        container_layout.addSpacing(10)

        # Crop radio buttons
        self.crop_group = QButtonGroup()

        self.coca_radio = QRadioButton("🍃 Coca Leaves (38 min)")
        self.coca_radio.setObjectName("crop_option")
        self.coca_radio.setFixedHeight(45)
        self.crop_group.addButton(self.coca_radio, 0)
        container_layout.addWidget(self.coca_radio)
        container_layout.addSpacing(8)

        self.marijuana_radio = QRadioButton("🌿 Marijuana (19 min)")
        self.marijuana_radio.setObjectName("crop_option")
        self.marijuana_radio.setFixedHeight(45)
        self.crop_group.addButton(self.marijuana_radio, 1)
        container_layout.addWidget(self.marijuana_radio)
        container_layout.addSpacing(25)

        # Planter Type Section
        planter_label = QLabel("Planter Choice")
        planter_label.setObjectName("section_title")
        planter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        planter_label.setFixedHeight(30)
        container_layout.addWidget(planter_label)
        container_layout.addSpacing(10)

        # Planter radio buttons
        self.planter_group = QButtonGroup()

        self.basic_planter_radio = QRadioButton("📦 Basic Planter (Standard time)")
        self.basic_planter_radio.setObjectName("planter_option")
        self.basic_planter_radio.setFixedHeight(45)
        self.planter_group.addButton(self.basic_planter_radio, 0)
        container_layout.addWidget(self.basic_planter_radio)
        container_layout.addSpacing(8)

        self.planter_box_radio = QRadioButton("🏗️ Planter Box (5% faster)")
        self.planter_box_radio.setObjectName("planter_option")
        self.planter_box_radio.setFixedHeight(45)
        self.planter_group.addButton(self.planter_box_radio, 1)
        container_layout.addWidget(self.planter_box_radio)
        container_layout.addSpacing(40)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel")
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("ok")
        self.save_btn.setFixedHeight(45)
        self.save_btn.setFixedWidth(100)
        self.save_btn.setDefault(True)  # Make it the default button
        self.save_btn.clicked.connect(self.save_preferences)
        button_layout.addWidget(self.save_btn)

        container_layout.addLayout(button_layout)

        # Add container to main layout
        main_layout.addWidget(self.container)

    def setup_styling(self):
        """Apply modern styling matching the trigger dialog theme."""
        self.setStyleSheet("""
            #container {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a3d2e, stop:0.5 #2d5a47, stop:1 #1a3d2e);
                border: 3px solid #4a7c59;
                border-radius: 20px;
            }

            #title {
                color: #e8f5e8;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-bottom: 8px;
            }

            #section_title {
                color: #e8f5e8;
                font-size: 17px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0px;
                padding: 8px 0;
                background: transparent;
                border: none;
                text-align: center;
                min-height: 30px;
                max-height: 30px;
            }

            #crop_option, #planter_option {
                color: #e8f5e8;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 500;
                padding: 12px 15px 12px 35px;
                margin: 0px;
                spacing: 8px;
                border: none;
                background: transparent;
            }

            #crop_option::indicator, #planter_option::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #4a7c59;
                background-color: #2d5a47;
                margin-right: 8px;
            }

            #crop_option::indicator:checked, #planter_option::indicator:checked {
                background-color: #6b9b73;
                border: 2px solid #7db87d;
            }

            #crop_option::indicator:hover, #planter_option::indicator:hover {
                border-color: #6b9b73;
                background-color: #3a6b54;
            }

            #crop_option:hover, #planter_option:hover {
                background-color: rgba(74, 124, 89, 0.15);
            }

            #crop_option:disabled, #planter_option:disabled {
                color: #666666;
                background-color: rgba(45, 90, 71, 0.3);
            }

            #crop_option::indicator:disabled, #planter_option::indicator:disabled {
                border-color: #666666;
                background-color: #444444;
            }

            #toggle_label {
                color: #e8f5e8;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 500;
                padding: 5px 0;
                margin: 0;
                background: transparent;
                border: none;
            }



            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a6b54, stop:1 #2d5a47);
                border: 2px solid #4a7c59;
                border-radius: 12px;
                padding: 12px 25px;
                color: #e8f5e8;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a7c59, stop:1 #3a6b54);
                border-color: #6b9b73;
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d5a47, stop:1 #1a3d2e);
            }

            #ok {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6b9b73, stop:1 #4a7c59);
                border-color: #6b9b73;
            }

            #ok:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7db87d, stop:1 #6b9b73);
                border-color: #7db87d;
            }

            #ok:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a7c59, stop:1 #3a6b54);
            }

            #cancel:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d32f2f, stop:1 #b71c1c);
                border-color: #d32f2f;
            }
        """)

    def center_on_screen(self):
        """Center the dialog on screen."""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        dialog_rect = self.geometry()
        x = (screen.width() - dialog_rect.width()) // 2
        y = (screen.height() - dialog_rect.height()) // 2
        self.move(x, y)
    

    
    def load_current_settings(self):
        """Load current settings into the dialog."""
        # Set auto-detection
        auto_detect = self.current_settings.get('auto_detect_crop', True)
        self.auto_detect_toggle.setChecked(auto_detect)

        # Set crop type
        if self.current_settings.get('crop_type') == 'marijuana':
            self.marijuana_radio.setChecked(True)
        else:
            self.coca_radio.setChecked(True)

        # Set planter type
        if self.current_settings.get('planter_type') == 'planter_box':
            self.planter_box_radio.setChecked(True)
        else:
            self.basic_planter_radio.setChecked(True)

        # Update UI state based on auto-detection
        self.on_auto_detect_toggled(auto_detect)

    def on_auto_detect_toggled(self, checked):
        """Handle auto-detection checkbox toggle."""
        # Enable/disable manual crop selection based on auto-detection
        self.coca_radio.setEnabled(not checked)
        self.marijuana_radio.setEnabled(not checked)

        # Visual feedback for enabled/disabled state
        if checked:
            print("🔍 Auto-detection enabled - manual crop selection disabled")
        else:
            print("👤 Manual mode enabled - auto-detection disabled")
    
    def save_preferences(self):
        """Save the preferences and emit signal."""
        try:
            crop_type = 'marijuana' if self.marijuana_radio.isChecked() else 'coca'
            planter_type = 'planter_box' if self.planter_box_radio.isChecked() else 'basic'
            auto_detect_crop = self.auto_detect_toggle.isChecked()

            preferences = {
                'crop_type': crop_type,
                'planter_type': planter_type,
                'auto_detect_crop': auto_detect_crop
            }

            print(f"💾 Saving preferences: {preferences}")
            self.preferences_saved.emit(preferences)
            self.accept()  # Close dialog

        except Exception as e:
            print(f"⚠️ Error saving preferences: {e}")
            # Still close the dialog even if there's an error
            self.accept()
