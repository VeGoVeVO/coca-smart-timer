#!/usr/bin/env python3
"""
Screenshot Tool for COCA Timer
Handles screen capture functionality using mss for fast screenshots.
"""

import numpy as np
from typing import Optional, Tuple

# Screenshot imports
try:
    import mss
    SCREENSHOT_AVAILABLE = True
    print("✅ Screenshot (mss) available")
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("⚠️ Screenshot not available - install mss")


class ScreenshotTool:
    """Fast screenshot capture tool using mss."""

    def __init__(self):
        """Initialize screenshot tool."""
        self.sct = None
        # Don't initialize mss here - do it per capture to avoid threading issues
    
    def capture_full_screen(self) -> Optional[np.ndarray]:
        """
        Capture full screen screenshot.

        Returns:
            Screenshot as numpy array or None if failed
        """
        if not SCREENSHOT_AVAILABLE:
            print("❌ Screenshot not available")
            return None

        try:
            # Create new mss instance to avoid threading issues
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = sct.grab(monitor)

                # Convert to numpy array
                img_array = np.array(screenshot)

                # Convert BGRA to RGB
                if img_array.shape[2] == 4:  # BGRA
                    img_array = img_array[:, :, [2, 1, 0]]  # BGR to RGB

                print(f"📸 Full screen captured: {img_array.shape}")
                return img_array

        except Exception as e:
            print(f"⚠️ Error capturing full screen: {e}")
            return None
    
    def capture_area(self, area: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Capture specific area of screen.

        Args:
            area: (x, y, width, height) tuple

        Returns:
            Screenshot as numpy array or None if failed
        """
        if not SCREENSHOT_AVAILABLE:
            print("❌ Screenshot not available")
            return None

        try:
            x, y, width, height = area

            # Define monitor region
            monitor = {
                "top": y,
                "left": x,
                "width": width,
                "height": height
            }

            # Create new mss instance to avoid threading issues
            with mss.mss() as sct:
                # Capture area
                screenshot = sct.grab(monitor)

                # Convert to numpy array
                img_array = np.array(screenshot)

                # Convert BGRA to RGB
                if img_array.shape[2] == 4:  # BGRA
                    img_array = img_array[:, :, [2, 1, 0]]  # BGR to RGB

                print(f"📸 Area captured: {img_array.shape} from {area}")
                return img_array

        except Exception as e:
            print(f"⚠️ Error capturing area {area}: {e}")
            return None
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get primary screen size.

        Returns:
            (width, height) tuple
        """
        if not SCREENSHOT_AVAILABLE:
            return (1920, 1080)  # Default fallback

        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                return (monitor["width"], monitor["height"])
        except Exception as e:
            print(f"⚠️ Error getting screen size: {e}")
            return (1920, 1080)  # Default fallback
