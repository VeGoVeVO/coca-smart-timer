#!/usr/bin/env python3
"""
COCA Timer - PyQt6 Floating Overlay for Fullscreen Games
Clean, minimal implementation with precise size control.
"""

import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QSystemTrayIcon, QMenu, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QLineEdit
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRect, QRectF, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction, QPainter, QPainterPath, QBrush, QColor, QPen, QCursor
from pynput import keyboard
import winsound
import threading
import time

# Handle both package and direct execution
try:
    # Package imports (when run as module)
    from .screenshot_tool import ScreenshotTool
    from .area_selector import AreaSelector
    from .coca_timer import CocaTimer
    from .preferences_dialog import PreferencesDialog
except ImportError:
    # Direct imports (when run directly)
    from screenshot_tool import ScreenshotTool
    from area_selector import AreaSelector
    from coca_timer import CocaTimer
    from preferences_dialog import PreferencesDialog


class ModernTriggerDialog(QDialog):
    """Modern, custom trigger word dialog with real-time validation."""

    def __init__(self, title, current_value, other_trigger, parent=None):
        super().__init__(parent)
        self.current_value = current_value
        self.other_trigger = other_trigger
        self.result_value = None

        self.setWindowTitle(title)
        self.setFixedSize(450, 320)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setup_ui()
        self.setup_styling()
        self.center_on_screen()

    def setup_ui(self):
        """Setup the modern UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main container
        self.container = QWidget()
        self.container.setObjectName("container")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(25)

        # Title
        self.title_label = QLabel("Change Trigger Word")
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.title_label)

        # Current value display
        self.current_label = QLabel(f"Current: '{self.current_value}'")
        self.current_label.setObjectName("current")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.current_label)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setObjectName("input")
        self.input_field.setText(self.current_value)
        self.input_field.setPlaceholderText("Enter new trigger word...")
        self.input_field.textChanged.connect(self.validate_input)
        self.input_field.returnPressed.connect(self.accept_if_valid)
        self.input_field.setMinimumHeight(50)  # Ensure proper height
        container_layout.addWidget(self.input_field)

        # Validation message
        self.validation_label = QLabel("")
        self.validation_label.setObjectName("validation")
        self.validation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.validation_label.setWordWrap(True)
        container_layout.addWidget(self.validation_label)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        # OK button
        self.ok_btn = QPushButton("Apply")
        self.ok_btn.setObjectName("ok")
        self.ok_btn.setMinimumHeight(45)
        self.ok_btn.setMinimumWidth(100)
        self.ok_btn.clicked.connect(self.on_apply_clicked)
        self.ok_btn.setEnabled(False)
        button_layout.addWidget(self.ok_btn)

        container_layout.addLayout(button_layout)
        layout.addWidget(self.container)

        # Focus on input
        self.input_field.setFocus()
        self.input_field.selectAll()

    def setup_styling(self):
        """Apply modern styling to the dialog."""
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

            #current {
                color: #b8d4b8;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-bottom: 15px;
            }

            #input {
                background-color: #2d5a47;
                border: 2px solid #4a7c59;
                border-radius: 12px;
                padding: 15px 20px;
                color: #e8f5e8;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 500;
                selection-background-color: #6b9b73;
            }

            #input:focus {
                border-color: #6b9b73;
                background-color: #3a6b54;
            }

            #validation {
                color: #ff8a80;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 25px;
                margin: 8px 0;
                font-weight: 500;
            }

            #validation[valid="true"] {
                color: #a5d6a7;
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

            #ok:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #333333, stop:1 #2a2a2a);
                border-color: #444444;
                color: #666666;
            }

            #cancel:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d32f2f, stop:1 #b71c1c);
                border-color: #d32f2f;
            }
        """)

    def validate_input(self):
        """Real-time validation with visual feedback."""
        text = self.input_field.text().strip().lower()

        # Check if empty
        if not text:
            self.show_validation("Enter a trigger word", False)
            return

        # Check length
        if len(text) < 2:
            self.show_validation("Must be at least 2 characters", False)
            return

        if len(text) > 10:
            self.show_validation("Must be 10 characters or less", False)
            return

        # Check characters
        if not text.isalpha():
            self.show_validation("Only letters allowed (a-z)", False)
            return

        # Check for spaces
        if ' ' in text:
            self.show_validation("No spaces allowed", False)
            return

        # Check for conflicts
        if text in self.other_trigger or self.other_trigger in text:
            self.show_validation(f"Conflicts with other trigger '{self.other_trigger}'", False)
            return

        # Check if same as current
        if text == self.current_value:
            self.show_validation("Same as current value", False)
            return

        # All good!
        self.show_validation("✓ Valid trigger word", True)

    def show_validation(self, message, is_valid):
        """Show validation message with appropriate styling."""
        self.validation_label.setText(message)
        self.validation_label.setProperty("valid", str(is_valid).lower())
        self.validation_label.style().unpolish(self.validation_label)
        self.validation_label.style().polish(self.validation_label)
        self.ok_btn.setEnabled(is_valid)

    def on_apply_clicked(self):
        """Handle Apply button click."""
        self.accept_if_valid()

    def accept_if_valid(self):
        """Accept dialog only if input is valid."""
        text = self.input_field.text().strip().lower()

        if self.ok_btn.isEnabled() and text:
            self.result_value = text
            self.accept()
        else:
            # Show feedback if trying to apply invalid input
            self.input_field.setFocus()
            self.input_field.selectAll()

    def keyPressEvent(self, event):
        """Handle ESC key to cancel."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def center_on_screen(self):
        """Center the dialog on the screen."""
        screen = QApplication.primaryScreen().geometry()
        dialog_size = self.size()
        x = (screen.width() - dialog_size.width()) // 2
        y = (screen.height() - dialog_size.height()) // 2
        self.move(x, y)


class RoundedLabel(QLabel):
    """Custom label with rounded background."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_color = QColor(200, 200, 200, 80)
        self.border_radius = 14  # Reduced from 18 to 14 (20% smaller)

    def set_background_color(self, color: QColor):
        """Set the background color."""
        self.bg_color = color
        self.update()

    def paintEvent(self, event):
        """Custom paint event for rounded background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create rounded rectangle path
        path = QPainterPath()
        rect = QRectF(self.rect())  # Convert QRect to QRectF
        path.addRoundedRect(rect, self.border_radius, self.border_radius)

        # Fill background
        painter.fillPath(path, QBrush(self.bg_color))

        # Draw border
        pen = QPen(QColor(255, 255, 255, 40))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)

        # Draw text
        painter.setPen(QColor(255, 255, 255, 255))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class CocaTimerOverlay(QWidget):
    """Minimal floating overlay with precise size control."""

    # Signal for thread-safe UI updates
    timer_update_signal = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        # Initialize position settings first
        self.position_mode = "center_top"  # Default position
        self.position_animation = None

        # Initialize trigger words
        self.trigger_start = "ccc"  # Default start trigger
        self.trigger_reset = "rrr"  # Default reset trigger

        # Configuration - save to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(project_dir, "coca_config.json")
        self.selected_area = None
        self.area_reset_requested = False

        # Growing preferences
        self.crop_type = "coca"  # coca or marijuana
        self.planter_type = "basic"  # basic or planter_box
        self.auto_detect_crop = True  # auto-detect crop type from screenshot

        self.load_config()  # Load config before setting up window

        self.setup_window()
        self.setup_ui()
        self.setup_components()
        self.setup_keyboard()

        # Connect signal for thread-safe updates
        self.timer_update_signal.connect(self.update_display)

        # Setup system tray
        self.setup_system_tray()

        print("🎯 COCA Timer Overlay started!")
        print(f"📋 Controls: '{self.trigger_start}' to start, '{self.trigger_reset}' to reset area")
    
    def setup_window(self):
        """Setup floating overlay window with dynamic dimensions."""
        # Window flags for floating overlay
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        # Initial size - will be adjusted dynamically
        self.setFixedSize(200, 40)  # Start smaller, will resize based on content

        # Position at top center of screen
        screen = QApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.position_window()

        # Transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Make non-interactive for gaming
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def position_window(self, animate=False):
        """Position window based on current position mode."""
        screen = QApplication.primaryScreen().geometry()
        margin = 20

        # Calculate position based on mode
        if self.position_mode == "center_top":
            x = (screen.width() - self.width()) // 2
            y = margin
        elif self.position_mode == "top_left":
            x = margin
            y = margin
        elif self.position_mode == "top_right":
            x = screen.width() - self.width() - margin
            y = margin
        elif self.position_mode == "bottom_center":
            x = (screen.width() - self.width()) // 2
            y = screen.height() - self.height() - margin
        elif self.position_mode == "bottom_left":
            x = margin
            y = screen.height() - self.height() - margin
        elif self.position_mode == "bottom_right":
            x = screen.width() - self.width() - margin
            y = screen.height() - self.height() - margin
        else:
            # Default to center_top
            x = (screen.width() - self.width()) // 2
            y = margin

        if animate and hasattr(self, 'position_animation'):
            # Smooth animation to new position
            if self.position_animation:
                self.position_animation.stop()

            self.position_animation = QPropertyAnimation(self, b"pos")
            self.position_animation.setDuration(300)  # 300ms smooth animation
            self.position_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.position_animation.setStartValue(self.pos())
            self.position_animation.setEndValue(QPoint(x, y))
            self.position_animation.start()
        else:
            self.move(x, y)
    
    def setup_ui(self):
        """Setup the text label with dynamic formatting."""
        self.label = RoundedLabel(self)

        # Font and styling - 20% smaller
        self.font = QFont("Consolas", 9, QFont.Weight.Bold)  # Reduced from 11 to 9
        self.label.setFont(self.font)

        # Center-align the text
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        # Initial text with full format
        self.current_time = "38:00"
        self.current_percentage = "0.00 %"
        self.current_crop_display = "Coca"  # Dynamic crop display name
        self.current_status = "Growing"  # Current stage status
        self.original_time = 38 * 60  # Store original time for percentage calculation
        self.detected_percentage = 0.0  # Store the initially detected percentage
        self.notifications_sent = set()  # Track which notifications have been sent
        self.flash_timer = QTimer()  # Timer for flashing effect
        self.flash_timer.timeout.connect(self.toggle_flash)
        self.is_flashing = False
        self.flash_state = False
        self.start_time = None  # Track when timer started for smooth percentage

        # Apply initial styling with default timer (38 minutes = 2280 seconds)
        self.update_display(38 * 60, "---")
    
    def setup_components(self):
        """Initialize core components."""
        self.screenshot_tool = ScreenshotTool()
        self.coca_timer = CocaTimer(self.timer_callback)
        self.area_selector = None

    def timer_callback(self, time_left: int, status: str):
        """Thread-safe callback for timer updates."""
        self.timer_update_signal.emit(time_left, status)

    def setup_system_tray(self):
        """Setup modern system tray with coca logo."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("⚠️ System tray not available")
            return

        # Load coca logo and make it 20% bigger
        # Handle both development and PyInstaller bundled paths
        if getattr(sys, 'frozen', False):
            # PyInstaller bundle
            base_path = sys._MEIPASS
            logo_path = os.path.join(base_path, "assets", "coca_logo.png")
        else:
            # Development
            logo_path = os.path.join(os.path.dirname(__file__), "assets", "coca_logo.png")
        if os.path.exists(logo_path):
            # Load and scale the image 20% bigger
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                # Calculate new size (20% bigger)
                original_size = pixmap.size()
                new_width = int(original_size.width() * 1.2)
                new_height = int(original_size.height() * 1.2)

                # Scale with smooth transformation
                scaled_pixmap = pixmap.scaled(
                    new_width, new_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                icon = QIcon(scaled_pixmap)
            else:
                icon = QIcon()
                print(f"⚠️ Could not load logo from: {logo_path}")
        else:
            # Fallback to default icon if logo not found
            icon = QIcon()
            print(f"⚠️ Logo not found at: {logo_path}")
            if getattr(sys, 'frozen', False):
                print(f"🔍 PyInstaller bundle detected. Base path: {sys._MEIPASS}")
                print(f"🔍 Available files in assets: {os.listdir(os.path.join(sys._MEIPASS, 'assets')) if os.path.exists(os.path.join(sys._MEIPASS, 'assets')) else 'assets folder not found'}")
            else:
                print(f"🔍 Development mode. Checking: {os.path.dirname(__file__)}")
                assets_dir = os.path.join(os.path.dirname(__file__), "assets")
                print(f"🔍 Assets directory exists: {os.path.exists(assets_dir)}")
                if os.path.exists(assets_dir):
                    print(f"🔍 Files in assets: {os.listdir(assets_dir)}")

        self.tray_icon = QSystemTrayIcon(icon, self)

        # Create modern context menu
        self.create_tray_menu()

        # Set tooltip
        self.tray_icon.setToolTip("COCA Smart Timer")

        # Connect activation signal for better menu positioning
        self.tray_icon.activated.connect(self.tray_icon_activated)

        # Show tray icon with explicit visibility
        self.tray_icon.show()
        self.tray_icon.setVisible(True)

        # Force tray icon to appear (helps with PyInstaller builds)
        QApplication.processEvents()

        print("✅ System tray initialized")
        print(f"🔍 Tray icon visible: {self.tray_icon.isVisible()}")
        print(f"🔍 System tray available: {QSystemTrayIcon.isSystemTrayAvailable()}")

    def create_tray_menu(self):
        """Create modern, professional tray menu."""
        menu = QMenu()

        # Coca leaf themed menu styling
        menu.setStyleSheet("""
            QMenu {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a3d2e, stop:0.5 #2d5a47, stop:1 #1a3d2e);
                border: 2px solid #4a7c59;
                border-radius: 12px;
                padding: 10px 0px;
                color: #e8f5e8;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: 500;
            }
            QMenu::item {
                padding: 10px 24px;
                margin: 3px 10px;
                border-radius: 8px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a7c59, stop:1 #3a6b54);
                color: #ffffff;
            }
            QMenu::item:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6b9b73, stop:1 #4a7c59);
            }
            QMenu::separator {
                height: 2px;
                background-color: #4a7c59;
                margin: 8px 16px;
                border-radius: 1px;
            }
        """)

        # Orientation submenu
        orientation_menu = QMenu("Orientation", menu)
        orientation_menu.setStyleSheet(menu.styleSheet())

        positions = [
            ("Center Top", "center_top"),
            ("Top Left", "top_left"),
            ("Top Right", "top_right"),
            ("Bottom Center", "bottom_center"),
            ("Bottom Left", "bottom_left"),
            ("Bottom Right", "bottom_right")
        ]

        for name, mode in positions:
            action = QAction(name, orientation_menu)
            action.setCheckable(True)
            action.setChecked(self.position_mode == mode)
            action.triggered.connect(lambda checked, m=mode: self.set_position_mode(m))
            orientation_menu.addAction(action)

        menu.addMenu(orientation_menu)
        menu.addSeparator()

        # Trigger words section
        trigger_menu = QMenu("Trigger Words", menu)
        trigger_menu.setStyleSheet(menu.styleSheet())

        # Start trigger action
        start_trigger_action = QAction(f"Start: '{self.trigger_start}'", trigger_menu)
        start_trigger_action.triggered.connect(self.change_start_trigger)
        trigger_menu.addAction(start_trigger_action)

        # Reset trigger action
        reset_trigger_action = QAction(f"Reset: '{self.trigger_reset}'", trigger_menu)
        reset_trigger_action.triggered.connect(self.change_reset_trigger)
        trigger_menu.addAction(reset_trigger_action)

        menu.addMenu(trigger_menu)
        menu.addSeparator()

        # Preferences action
        preferences_action = QAction("🌿 Preferences", menu)
        preferences_action.triggered.connect(self.show_preferences)
        menu.addAction(preferences_action)

        menu.addSeparator()

        # Exit action
        exit_action = QAction("❌ Exit", menu)
        exit_action.triggered.connect(self.exit_application)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.context_menu = menu  # Store reference for positioning

    def tray_icon_activated(self, reason):
        """Handle tray icon activation with proper menu positioning."""
        if reason == QSystemTrayIcon.ActivationReason.Context:
            # Get tray icon geometry for better positioning
            tray_geometry = self.tray_icon.geometry()
            menu = self.context_menu
            menu_size = menu.sizeHint()
            screen_geometry = QApplication.primaryScreen().availableGeometry()

            # Position menu above the tray icon
            if tray_geometry.isValid():
                # Use tray icon position
                x = tray_geometry.center().x() - menu_size.width() // 2
                y = tray_geometry.top() - menu_size.height() - 5  # 5px gap above tray
            else:
                # Fallback to cursor position if tray geometry not available
                cursor_pos = QCursor.pos()
                x = cursor_pos.x() - menu_size.width() // 2
                y = cursor_pos.y() - menu_size.height() - 10

            # Ensure menu stays within screen bounds
            if x + menu_size.width() > screen_geometry.right():
                x = screen_geometry.right() - menu_size.width()
            if x < screen_geometry.left():
                x = screen_geometry.left()
            if y < screen_geometry.top():
                y = screen_geometry.top()
            if y + menu_size.height() > screen_geometry.bottom():
                y = screen_geometry.bottom() - menu_size.height()

            menu.popup(QPoint(x, y))

    def set_position_mode(self, mode):
        """Set overlay position mode with smooth animation."""
        if self.position_mode != mode:
            self.position_mode = mode
            self.position_window(animate=True)
            self.save_config()  # Save position preference

            # Update menu checkmarks
            self.create_tray_menu()

            print(f"🎯 Position changed to: {mode}")

    def change_start_trigger(self):
        """Change the start trigger word via modern dialog."""
        dialog = ModernTriggerDialog(
            "Change Start Trigger",
            self.trigger_start,
            self.trigger_reset,
            self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_value:
            self.trigger_start = dialog.result_value
            self.save_config()
            self.restart_keyboard_listener()  # Restart listener with new triggers
            self.create_tray_menu()  # Refresh menu
            print(f"✅ Start trigger changed to: '{self.trigger_start}'")

    def change_reset_trigger(self):
        """Change the reset trigger word via modern dialog."""
        dialog = ModernTriggerDialog(
            "Change Reset Trigger",
            self.trigger_reset,
            self.trigger_start,
            self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_value:
            self.trigger_reset = dialog.result_value
            self.save_config()
            self.restart_keyboard_listener()  # Restart listener with new triggers
            self.create_tray_menu()  # Refresh menu
            print(f"✅ Reset trigger changed to: '{self.trigger_reset}'")



    def exit_application(self):
        """Clean exit of the application."""
        print("👋 COCA Timer exiting...")
        if hasattr(self, 'coca_timer'):
            self.coca_timer.stop()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        QApplication.quit()
    
    def setup_keyboard(self):
        """Setup global keyboard listener."""
        self.key_sequence = []
        
        def on_key_press(key):
            try:
                if hasattr(key, 'char') and key.char:
                    self.key_sequence.append(key.char.lower())
                    
                    # Keep only the necessary characters based on longest trigger word
                    max_trigger_len = max(len(self.trigger_start), len(self.trigger_reset))
                    if len(self.key_sequence) > max_trigger_len:
                        self.key_sequence = self.key_sequence[-max_trigger_len:]
                    
                    # Check for trigger sequences (prioritize longer matches to avoid conflicts)
                    triggers_to_check = [
                        (self.trigger_start, "start", self.handle_start_trigger),
                        (self.trigger_reset, "reset", self.handle_reset_trigger)
                    ]

                    # Sort by length (longest first) to prioritize longer matches
                    triggers_to_check.sort(key=lambda x: len(x[0]), reverse=True)

                    for trigger_word, trigger_type, handler in triggers_to_check:
                        if len(self.key_sequence) >= len(trigger_word):
                            sequence = ''.join(self.key_sequence[-len(trigger_word):])
                            if sequence == trigger_word:
                                print(f"🎯 {trigger_type.title()} trigger '{trigger_word}' detected!")
                                handler()
                                self.key_sequence = []
                                return
            except Exception as e:
                print(f"⚠️ Keyboard error: {e}")
        
        self.keyboard_listener = keyboard.Listener(on_press=on_key_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def restart_keyboard_listener(self):
        """Restart keyboard listener with updated trigger words."""
        try:
            # Stop existing listener
            if hasattr(self, 'keyboard_listener') and self.keyboard_listener:
                self.keyboard_listener.stop()
                print("🔄 Stopped old keyboard listener")

            # Start new listener with updated triggers
            self.setup_keyboard()
            print("✅ Restarted keyboard listener with new triggers")
        except Exception as e:
            print(f"⚠️ Error restarting keyboard listener: {e}")
    
    def update_text(self):
        """Update the display text with consistent formatting."""
        text = f"{self.current_crop_display}: {self.current_time} | {self.current_percentage} | {self.current_status}"
        self.label.setText(text)

        # Force the label to calculate its size with current styling
        self.label.adjustSize()

        # Calculate size based on text metrics for perfect fit
        font_metrics = self.label.fontMetrics()
        text_width = font_metrics.horizontalAdvance(text)
        text_height = font_metrics.height()

        # Add padding for the rounded background - 20% smaller
        window_width = max(text_width + 16, 96)    # Reduced padding (20→16, 120→96)
        window_height = max(text_height + 10, 28)  # Reduced padding (12→10, 35→28)

        self.setFixedSize(window_width, window_height)
        self.label.resize(window_width, window_height)
        self.position_window()  # Re-center after resize

    def toggle_flash(self):
        """Toggle flash state for flashing effect."""
        self.flash_state = not self.flash_state
        # Force a display update to show the flash
        if hasattr(self, 'current_time'):
            self.update_text()

    def play_beep(self, count: int):
        """Play beep sound in a separate thread."""
        def beep_thread():
            for _ in range(count):
                winsound.Beep(800, 200)  # 800Hz for 200ms
                if count > 1:
                    threading.Event().wait(0.3)  # Short pause between beeps

        threading.Thread(target=beep_thread, daemon=True).start()

    def play_completion_sound(self):
        """Play a nature-inspired completion sound that fits the coca leaf theme."""
        def completion_thread():
            try:
                # Nature-inspired completion melody - like wind through leaves
                winsound.Beep(440, 200)  # A4 - natural, earthy tone
                threading.Event().wait(0.08)
                winsound.Beep(523, 180)  # C5 - gentle rise
                threading.Event().wait(0.06)
                winsound.Beep(659, 220)  # E5 - harmonious completion
            except Exception as e:
                print(f"⚠️ Error playing completion sound: {e}")

        threading.Thread(target=completion_thread, daemon=True).start()

    def update_display(self, time_left: int, status: str = ""):
        """Update the timer display with multi-stage lifecycle support."""

        # Update current status (filter out stage completion signals)
        if status.startswith("stage_completed_"):
            # Don't update display status for completion signals, just handle sound
            return
        self.current_status = status if status else "Growing"

        # Handle different stages
        if status == "Seeding":
            # Seeding stage shows infinity symbol
            self.current_time = "∞"
            self.current_percentage = "100.00 %"
        elif status in ["Ready", "Flowering"]:
            # Ready and Flowering stages show countdown timer
            if time_left >= 0:
                minutes = time_left // 60
                seconds = time_left % 60
                self.current_time = f"{minutes:02d}:{seconds:02d}"
            else:
                self.current_time = "00:00"

            # For non-growing stages, show 100% (plant is fully grown)
            self.current_percentage = "100.00 %"
        else:
            # Growing stage - normal timer with percentage progression
            minutes = time_left // 60
            seconds = time_left % 60
            self.current_time = f"{minutes:02d}:{seconds:02d}"

            # Calculate live percentage based on time remaining during growing stage
            if hasattr(self, 'original_time') and self.original_time > 0 and status == "Growing":
                # Use real time for ultra-smooth percentage progression
                if self.start_time is None:
                    self.start_time = time.time()

                # Calculate actual time elapsed since timer started
                current_time = time.time()
                real_time_elapsed = current_time - self.start_time

                # Calculate the percentage range we need to cover (from detected to 100%)
                percentage_range = 100.0 - self.detected_percentage

                # Calculate progress through the remaining percentage using real time
                if self.original_time > 0:
                    progress_ratio = min(real_time_elapsed / self.original_time, 1.0)
                    percentage_increase = percentage_range * progress_ratio
                    current_percentage = self.detected_percentage + percentage_increase
                else:
                    current_percentage = self.detected_percentage

                self.current_percentage = f"{current_percentage:.2f} %"
            else:
                self.current_percentage = f"{self.detected_percentage:.2f} %"

        # Handle stage completion sounds
        if status.startswith("stage_completed_"):
            stage_name = status.replace("stage_completed_", "")
            if status not in self.notifications_sent:
                self.notifications_sent.add(status)
                self.play_completion_sound()
                self.stop_flashing()
                print(f"🔊 {stage_name.title()} stage completed - playing completion sound")
            return  # Don't process further for stage completion signals

        # Handle notifications and flashing (only for timed stages)
        if status != "Seeding" and time_left >= 0:
            # Check if we just entered a new stage and stop flashing
            stage_key = f"{status}_stage"
            if stage_key not in self.notifications_sent:
                self.notifications_sent.add(stage_key)
                self.stop_flashing()  # Stop flashing when entering new stage

            if time_left == 300 and f"{status}_5min" not in self.notifications_sent:  # 5 minutes
                self.notifications_sent.add(f"{status}_5min")
                self.play_beep(1)
                self.start_flashing()
            elif time_left == 60 and f"{status}_1min" not in self.notifications_sent:  # 1 minute
                self.notifications_sent.add(f"{status}_1min")
                self.play_beep(2)
                self.start_flashing()
            elif time_left == 0 and f"{status}_completed" not in self.notifications_sent:  # Stage completed
                self.notifications_sent.add(f"{status}_completed")
                self.play_completion_sound()
                self.stop_flashing()

        # Update background colors based on stage and time left
        if status == "Seeding":
            # Seeding stage - special green color to indicate completion
            base_color = QColor(76, 175, 80, 120)  # Green for seeding
            self.stop_flashing()
        elif status == "Flowering":
            # Flowering stage - purple/pink color, only flash in warning periods
            if time_left <= 60:  # Last minute - red background with flashing
                base_color = QColor(255, 68, 68, 120)
            elif time_left <= 300:  # Last 5 minutes - orange warning
                base_color = QColor(255, 165, 0, 120)
            else:  # Normal flowering - purple background, no flashing
                base_color = QColor(156, 39, 176, 120)
                if time_left > 300:  # Stop flashing if not in warning period
                    self.stop_flashing()
        elif status == "Ready":
            # Ready stage - blue color, only flash in warning periods
            if time_left <= 60:  # Last minute - red background with flashing
                base_color = QColor(255, 68, 68, 120)
            elif time_left <= 300:  # Last 5 minutes - orange warning
                base_color = QColor(255, 165, 0, 120)
            else:  # Normal ready - blue background, no flashing
                base_color = QColor(33, 150, 243, 120)
                if time_left > 300:  # Stop flashing if not in warning period
                    self.stop_flashing()
        elif time_left <= 60:  # Last minute - red background
            base_color = QColor(255, 68, 68, 120)
        elif time_left <= 300:  # Last 5 minutes - orange-yellow warning background
            base_color = QColor(255, 165, 0, 120)  # Orange-yellow warning color
        else:  # Normal growing - light grey background
            base_color = QColor(200, 200, 200, 80)
            self.stop_flashing()  # Stop flashing when not in warning time

        # Apply flashing effect if active
        if self.is_flashing and self.flash_state:
            bg_color = QColor(255, 255, 255, 150)  # Flash to white
        else:
            bg_color = base_color

        # Set the background color on our custom rounded label
        self.label.set_background_color(bg_color)

        # Remove any stylesheet to let custom painting handle everything
        self.label.setStyleSheet("")
        self.update_text()

        # Ensure overlay is visible and on top
        if not self.isVisible():
            self.show()
        self.raise_()
        self.activateWindow()

    def start_flashing(self):
        """Start the elegant, slow flashing effect."""
        if not self.is_flashing:
            self.is_flashing = True
            self.flash_timer.start(1200)  # Slow, elegant flash every 1.2 seconds

    def stop_flashing(self):
        """Stop the flashing effect."""
        if self.is_flashing:
            self.is_flashing = False
            self.flash_state = False
            self.flash_timer.stop()

    def handle_start_trigger(self):
        """Handle start trigger - start timer or area selection."""
        print(f"🎯 '{self.trigger_start}' triggered")

        # Prevent rapid trigger firing
        if hasattr(self, '_last_start_trigger') and time.time() - self._last_start_trigger < 1.0:
            print("⚠️ Start trigger fired too quickly - ignoring")
            return
        self._last_start_trigger = time.time()

        if not self.selected_area or self.area_reset_requested:
            print("📍 Selecting area...")
            self.select_area()
        else:
            self.start_timer()

    def handle_reset_trigger(self):
        """Handle reset trigger - reset area selection."""
        print(f"🔄 '{self.trigger_reset}' triggered - area reset requested")

        # Prevent rapid trigger firing
        if hasattr(self, '_last_reset_trigger') and time.time() - self._last_reset_trigger < 1.0:
            print("⚠️ Reset trigger fired too quickly - ignoring")
            return
        self._last_reset_trigger = time.time()

        # Stop any running timer
        try:
            if hasattr(self, 'coca_timer') and self.coca_timer.running:
                self.coca_timer.stop()
                print("⏹️ Timer stopped for area reset")
        except Exception as e:
            print(f"⚠️ Error stopping timer: {e}")

        # Force cleanup of any existing area selector
        self._cleanup_area_selector()

        # Clear area and request reset
        self.selected_area = None
        self.area_reset_requested = True
        self._selecting_area = False  # Reset selection flag
        print("✅ Area reset - use start trigger to select new area")

    def _cleanup_area_selector(self):
        """Force cleanup of area selector to prevent crashes."""
        try:
            if hasattr(self, 'area_selector') and self.area_selector:
                print("🧹 Cleaning up existing area selector...")
                self.area_selector.cleanup_and_close()
                self.area_selector = None
                print("✅ Area selector cleaned up")
        except Exception as e:
            print(f"⚠️ Error in area selector cleanup: {e}")
            self.area_selector = None
    
    def select_area(self):
        """Open area selector for OCR region - robust version."""
        # Prevent multiple simultaneous area selections
        if hasattr(self, '_selecting_area') and self._selecting_area:
            print("⚠️ Area selection already in progress...")
            return

        self._selecting_area = True

        try:
            print("📸 Preparing area selection...")

            # Take screenshot with retries
            screenshot = None
            for attempt in range(3):
                try:
                    screenshot = self.screenshot_tool.capture_full_screen()
                    if screenshot is not None:
                        print(f"✅ Screenshot for area selection captured (attempt {attempt + 1})")
                        break
                    else:
                        print(f"⚠️ Screenshot attempt {attempt + 1} failed - retrying...")
                        time.sleep(0.2)
                except Exception as e:
                    print(f"⚠️ Screenshot attempt {attempt + 1} error: {e}")
                    time.sleep(0.2)

            if screenshot is None:
                print("❌ Failed to capture screenshot for area selection after all attempts")
                self._selecting_area = False
                return

            # Hide main window temporarily
            self.hide()

            def on_area_selected(area):
                try:
                    self.selected_area = area
                    self.area_reset_requested = False
                    self.save_config()
                    self.show()
                    print(f"✅ COCA area selected: {area}")
                except Exception as e:
                    print(f"⚠️ Error saving selected area: {e}")
                    self.show()
                finally:
                    self._selecting_area = False

            def on_cancelled():
                try:
                    self.show()
                    print("❌ Area selection cancelled")
                except Exception as e:
                    print(f"⚠️ Error handling cancelled selection: {e}")
                finally:
                    self._selecting_area = False

            # Clean up any existing area selector
            self._cleanup_area_selector()

            self.area_selector = AreaSelector(screenshot, on_area_selected, on_cancelled)

            # Run area selector in separate thread to avoid blocking main app
            def run_area_selector():
                try:
                    self.area_selector.show()
                except Exception as e:
                    print(f"⚠️ Error running area selector: {e}")
                    self.show()  # Show main window if area selector fails
                    self._selecting_area = False

            selector_thread = threading.Thread(target=run_area_selector, daemon=True)
            selector_thread.start()
            print("🎯 Area selector thread started - select the percentage area")

        except Exception as e:
            print(f"⚠️ Critical error in area selection: {e}")
            self.show()
            self._selecting_area = False
    
    def start_timer(self):
        """Start the COCA timer with OCR detection - robust version."""
        if not self.selected_area:
            print("❌ No area selected - use reset trigger then start trigger")
            return

        # Prevent multiple simultaneous timer starts
        if hasattr(self, '_starting_timer') and self._starting_timer:
            print("⚠️ Timer start already in progress...")
            return

        self._starting_timer = True

        try:
            print("📸 Capturing screenshot...")
            screenshot = None

            # Robust screenshot capture with retries
            for attempt in range(3):
                try:
                    screenshot = self.screenshot_tool.capture_area(self.selected_area)
                    if screenshot is not None:
                        print(f"✅ Screenshot captured (attempt {attempt + 1})")
                        break
                    else:
                        print(f"⚠️ Screenshot attempt {attempt + 1} failed - retrying...")
                        time.sleep(0.1)  # Brief pause before retry
                except Exception as e:
                    print(f"⚠️ Screenshot attempt {attempt + 1} error: {e}")
                    time.sleep(0.1)

            if screenshot is None:
                print("❌ All screenshot attempts failed - using default timer")
                self._start_default_timer()
                return

            print("🔍 Running OCR detection...")
            percentage = None
            detected_crop = None

            # Robust OCR with error handling
            try:
                if self.auto_detect_crop:
                    # Use enhanced detection that also extracts crop type
                    percentage, detected_crop = self.coca_timer.detect_percentage_and_crop(screenshot)

                    # If crop type was detected, use it to override manual setting
                    if detected_crop:
                        original_crop = self.crop_type
                        self.crop_type = detected_crop
                        # Update display name for floating UI
                        self.current_crop_display = "Cannabis" if detected_crop == "marijuana" else "Coca"
                        print(f"🌿 Auto-detected crop type: {detected_crop} (was: {original_crop})")
                    else:
                        # Use manual setting and update display name
                        self.current_crop_display = "Cannabis" if self.crop_type == "marijuana" else "Coca"
                        print(f"🌿 No crop type detected, using manual setting: {self.crop_type}")
                else:
                    # Use standard percentage detection only
                    percentage = self.coca_timer.detect_percentage(screenshot)
                    # Update display name for manual setting
                    self.current_crop_display = "Cannabis" if self.crop_type == "marijuana" else "Coca"
                    print(f"🌿 Using manual crop setting: {self.crop_type}")

            except Exception as e:
                print(f"⚠️ OCR detection failed: {e}")
                percentage = None
                detected_crop = None

            if percentage is not None:
                timer_seconds = self.get_timer_duration(percentage)
                timer_seconds = max(1, timer_seconds)  # Minimum 1 second

                crop_name = "Coca" if self.crop_type == "coca" else "Marijuana"
                planter_name = "Basic" if self.planter_type == "basic" else "Planter Box"
                print(f"🔍 {crop_name} OCR: Detected {percentage}% - {planter_name} timer set to {timer_seconds//60}:{timer_seconds%60:02d}")

                # Store detected percentage and set original time for percentage calculation
                self.detected_percentage = percentage
                self.original_time = timer_seconds
                self.start_time = None  # Reset start time for smooth percentage

                # Start timer with error handling
                try:
                    # Reset notifications for new timer
                    self.notifications_sent.clear()
                    self.stop_flashing()  # Stop any existing flashing
                    self.coca_timer.start(timer_seconds, self.crop_type, self.planter_type)
                except Exception as e:
                    print(f"⚠️ Timer start failed: {e}")
                    self._start_default_timer()
            else:
                print("❌ Could not detect percentage - using default 38 minute timer")
                self._start_default_timer()

        except Exception as e:
            print(f"⚠️ Critical error in start_timer: {e}")
            self._start_default_timer()
        finally:
            self._starting_timer = False

    def _start_default_timer(self):
        """Start default timer based on preferences with error handling."""
        try:
            self.detected_percentage = 0.0
            default_seconds = self.get_timer_duration(0.0)  # 0% = full timer
            self.original_time = default_seconds
            self.start_time = None
            # Reset notifications for new timer
            self.notifications_sent.clear()
            self.stop_flashing()  # Stop any existing flashing
            self.coca_timer.start(default_seconds, self.crop_type, self.planter_type)

            crop_name = "Coca" if self.crop_type == "coca" else "Marijuana"
            planter_name = "Basic" if self.planter_type == "basic" else "Planter Box"
            print(f"🎯 {crop_name} timer started: {default_seconds//60}:{default_seconds%60:02d} ({planter_name} - default)")
        except Exception as e:
            print(f"⚠️ Even default timer failed: {e}")
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if 'selected_area' in config:
                        self.selected_area = tuple(config['selected_area'])
                        print(f"✅ Loaded COCA area: {self.selected_area}")
                    if 'position_mode' in config:
                        self.position_mode = config['position_mode']
                        print(f"✅ Loaded position: {self.position_mode}")
                    if 'trigger_start' in config:
                        self.trigger_start = config['trigger_start']
                        print(f"✅ Loaded start trigger: '{self.trigger_start}'")
                    if 'trigger_reset' in config:
                        self.trigger_reset = config['trigger_reset']
                        print(f"✅ Loaded reset trigger: '{self.trigger_reset}'")
                    if 'crop_type' in config:
                        self.crop_type = config['crop_type']
                        print(f"✅ Loaded crop type: '{self.crop_type}'")
                    if 'planter_type' in config:
                        self.planter_type = config['planter_type']
                        print(f"✅ Loaded planter type: '{self.planter_type}'")
                    if 'auto_detect_crop' in config:
                        self.auto_detect_crop = config['auto_detect_crop']
                        print(f"✅ Loaded auto-detect crop: {self.auto_detect_crop}")
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file."""
        try:
            config = {}
            if self.selected_area:
                config['selected_area'] = list(self.selected_area)
            config['position_mode'] = self.position_mode
            config['trigger_start'] = self.trigger_start
            config['trigger_reset'] = self.trigger_reset
            config['crop_type'] = self.crop_type
            config['planter_type'] = self.planter_type
            config['auto_detect_crop'] = self.auto_detect_crop

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Saved COCA config")
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")

    def show_preferences(self):
        """Show preferences dialog."""
        try:
            current_settings = {
                'crop_type': self.crop_type,
                'planter_type': self.planter_type,
                'auto_detect_crop': self.auto_detect_crop
            }

            dialog = PreferencesDialog(self, current_settings)
            dialog.preferences_saved.connect(self.on_preferences_saved)
            dialog.exec()
        except Exception as e:
            print(f"⚠️ Error showing preferences: {e}")

    def on_preferences_saved(self, preferences):
        """Handle saved preferences."""
        try:
            self.crop_type = preferences['crop_type']
            self.planter_type = preferences['planter_type']
            self.auto_detect_crop = preferences['auto_detect_crop']

            # Update display name for floating UI
            self.current_crop_display = "Cannabis" if self.crop_type == "marijuana" else "Coca"

            # Save to config
            self.save_config()

            auto_status = "enabled" if self.auto_detect_crop else "disabled"
            print(f"✅ Preferences updated: {self.crop_type} in {self.planter_type}, auto-detect {auto_status}")

            # Update tray menu to reflect changes
            self.create_tray_menu()

        except Exception as e:
            print(f"⚠️ Error saving preferences: {e}")

    def get_timer_duration(self, percentage):
        """Calculate timer duration based on crop type, planter type, and percentage."""
        try:
            # Base times in minutes
            if self.crop_type == "coca":
                base_time = 38.0 if self.planter_type == "basic" else 36.0
            else:  # marijuana
                base_time = 19.0 if self.planter_type == "basic" else 18.0

            # Calculate remaining time based on percentage
            remaining_percentage = 100.0 - percentage
            remaining_time = (remaining_percentage / 100.0) * base_time

            # Convert to seconds
            return int(remaining_time * 60)

        except Exception as e:
            print(f"⚠️ Error calculating timer duration: {e}")
            return 38 * 60  # Default fallback


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("COCA Smart Timer")
    app.setApplicationVersion("1.0.3")
    app.setOrganizationName("COCA Timer")

    # Ensure app doesn't quit when overlay is hidden
    app.setQuitOnLastWindowClosed(False)

    # Create and show overlay
    overlay = CocaTimerOverlay()
    overlay.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
