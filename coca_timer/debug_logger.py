"""
Debug logging utility for COCA Smart Timer.
Provides detailed logging for OCR detection and screenshot analysis.
"""

import os
import sys
import logging
import datetime
from pathlib import Path
from typing import Optional, Any
import numpy as np
from PIL import Image


class DebugLogger:
    """Enhanced debug logger for OCR and screenshot analysis."""
    
    def __init__(self):
        """Initialize debug logger."""
        self.logger = None
        self.screenshots_dir = None
        self.setup_logging()
        self.setup_screenshots_dir()
    
    def setup_logging(self):
        """Setup detailed logging to debug.log file."""
        try:
            # Get the directory where the script/exe is located
            if getattr(sys, 'frozen', False):
                # Running as exe
                app_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            log_file = os.path.join(app_dir, 'debug.log')
            
            # Create logger
            self.logger = logging.getLogger('coca_debug')
            self.logger.setLevel(logging.DEBUG)
            
            # Remove existing handlers
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
            
            # Create file handler
            file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
            
            self.log("DEBUG", f"Debug logging initialized: {log_file}")
            
        except Exception as e:
            print(f"⚠️ Failed to setup debug logging: {e}")
    
    def setup_screenshots_dir(self):
        """Setup screenshots directory."""
        try:
            # Get the directory where the script/exe is located
            if getattr(sys, 'frozen', False):
                # Running as exe
                app_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            self.screenshots_dir = os.path.join(app_dir, 'screenshots')
            
            # Create directory if it doesn't exist
            os.makedirs(self.screenshots_dir, exist_ok=True)
            
            self.log("DEBUG", f"Screenshots directory: {self.screenshots_dir}")
            
        except Exception as e:
            self.log("ERROR", f"Failed to setup screenshots directory: {e}")
    
    def log(self, level: str, message: str):
        """Log a message with timestamp."""
        if self.logger:
            getattr(self.logger, level.lower())(message)
        else:
            print(f"[{level}] {message}")
    
    def log_screenshot_capture(self, success: bool, area: tuple = None, error: str = None):
        """Log screenshot capture attempt."""
        if success:
            if area:
                self.log("INFO", f"✅ Screenshot captured successfully - Area: {area}")
            else:
                self.log("INFO", "✅ Full screenshot captured successfully")
        else:
            self.log("ERROR", f"❌ Screenshot capture failed: {error}")
    
    def save_debug_screenshot(self, image: np.ndarray, prefix: str = "debug") -> Optional[str]:
        """Save screenshot for debugging (only keeps latest, replaces previous)."""
        if self.screenshots_dir is None or image is None:
            return None

        try:
            # Clear existing screenshots with same prefix (remove timestamp versions)
            for file in os.listdir(self.screenshots_dir):
                if file.startswith(f"{prefix}_") or file == f"{prefix}.png":
                    os.remove(os.path.join(self.screenshots_dir, file))

            # Save new screenshot without timestamp - just replace the previous one
            filename = f"{prefix}.png"
            filepath = os.path.join(self.screenshots_dir, filename)

            # Convert numpy array to PIL Image and save
            if len(image.shape) == 3:
                pil_image = Image.fromarray(image.astype('uint8'))
            else:
                pil_image = Image.fromarray(image.astype('uint8')).convert('RGB')

            pil_image.save(filepath)

            self.log("DEBUG", f"📸 Debug screenshot saved: {filename}")
            return filepath

        except Exception as e:
            self.log("ERROR", f"Failed to save debug screenshot: {e}")
            return None
    
    def log_ocr_attempt(self, method: str, config: str, text: str, success: bool):
        """Log OCR detection attempt."""
        status = "✅" if success else "❌"
        self.log("INFO", f"{status} OCR Method: {method} | Config: {config}")
        self.log("DEBUG", f"   Raw OCR Text: '{text.strip()}'" if text else "   No text detected")
    
    def log_percentage_extraction(self, text: str, percentages: list, method: str):
        """Log percentage extraction results."""
        if percentages:
            self.log("INFO", f"🔍 {method} found percentages: {percentages}")
        else:
            self.log("WARNING", f"❌ {method} found no percentages in: '{text.strip()}'")
    
    def log_image_processing(self, step: str, success: bool, details: str = ""):
        """Log image processing steps."""
        status = "✅" if success else "❌"
        self.log("DEBUG", f"{status} Image Processing - {step}: {details}")
    
    def log_final_result(self, percentage: Optional[float], method: str = ""):
        """Log final OCR result."""
        if percentage is not None:
            self.log("INFO", f"🎯 FINAL RESULT: {percentage}% detected using {method}")
        else:
            self.log("ERROR", "❌ FINAL RESULT: No percentage detected by any method")


# Global debug logger instance
debug_logger = DebugLogger()
