#!/usr/bin/env python3
"""
COCA Timer Core Module
Handles OCR percentage detection and countdown timer functionality.
"""

import threading
import time
import re
from typing import Optional, List, Callable
import numpy as np
from PIL import Image, ImageEnhance

# OCR imports
try:
    import pytesseract
    OCR_AVAILABLE = True
    print("✅ OCR (pytesseract) available")
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ OCR not available - install pytesseract")

# Audio removed for clean minimal implementation


class CocaTimer:
    """COCA Timer with OCR percentage detection."""

    def __init__(self, update_callback: Callable[[int, str], None]):
        """
        Initialize COCA timer.

        Args:
            update_callback: Function to call with (time_left, status) updates
        """
        self.update_callback = update_callback
        self.timer_thread = None
        self.running = False
        self.time_left = 38 * 60  # Default 38 minutes
        self.original_time = 38 * 60
        self.notifications_sent = set()  # Track sent notifications

        # Setup tesseract path if needed
        self.setup_tesseract()
    
    def setup_tesseract(self):
        """Setup tesseract path for Windows."""
        if not OCR_AVAILABLE:
            return
            
        import os
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            "tesseract"  # If it's in PATH
        ]
        
        for path in tesseract_paths:
            if path == "tesseract" or os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Tesseract found at: {path}")
                break
    
    def detect_percentage(self, image: np.ndarray) -> Optional[float]:
        """
        Detect percentage from image using OCR.
        
        Args:
            image: Screenshot image as numpy array
            
        Returns:
            Detected percentage value or None if not found
        """
        if not OCR_AVAILABLE:
            print("❌ OCR not available")
            return None

        if image is None:
            print("⚠️ No image provided for OCR")
            return None

        try:
            # Validate image
            if not isinstance(image, np.ndarray) or image.size == 0:
                print("⚠️ Invalid image for OCR")
                return None

            # Convert to PIL Image with error handling
            pil_image = None
            try:
                if len(image.shape) == 3:
                    pil_image = Image.fromarray(image.astype('uint8'))
                else:
                    pil_image = Image.fromarray(image.astype('uint8')).convert('RGB')
            except Exception as e:
                print(f"⚠️ Error converting image: {e}")
                return None

            if pil_image is None:
                print("⚠️ Failed to create PIL image")
                return None

            # Enhance image for better OCR with error handling
            enhanced_image = None
            try:
                enhanced_image = self.enhance_image_for_ocr(pil_image)
            except Exception as e:
                print(f"⚠️ Error enhancing image, using original: {e}")
                enhanced_image = pil_image

            # Perform OCR with multiple attempts and configurations
            text = ""
            ocr_configs = [
                '--psm 6 -c tessedit_char_whitelist=0123456789%',
                '--psm 8 -c tessedit_char_whitelist=0123456789%',
                '--psm 7 -c tessedit_char_whitelist=0123456789%'
            ]

            for config in ocr_configs:
                try:
                    text = pytesseract.image_to_string(enhanced_image, config=config)
                    if text and '%' in text:
                        break  # Found text with percentage, use this result
                except Exception as e:
                    print(f"⚠️ OCR attempt failed with config {config}: {e}")
                    continue

            if not text:
                print("❌ All OCR attempts failed")
                return None

            # Extract percentages with error handling
            percentages = []
            try:
                percentages = self.extract_percentages(text)
            except Exception as e:
                print(f"⚠️ Error extracting percentages: {e}")
                return None

            if percentages:
                # Take the smallest percentage (as requested in original)
                min_percentage = min(percentages)
                print(f"🔍 Found percentages: {percentages} - Using: {min_percentage}%")
                return min_percentage
            else:
                print(f"❌ No percentages found in OCR text: '{text.strip()}'")
                return None

        except Exception as e:
            print(f"⚠️ Critical OCR detection error: {e}")
            return None
    
    def enhance_image_for_ocr(self, img: Image.Image) -> Image.Image:
        """Enhance image for better OCR accuracy."""
        try:
            # Convert to grayscale
            img = img.convert('L')
            
            # Increase contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Scale up for better OCR
            width, height = img.size
            img = img.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
            
            return img
        except Exception as e:
            print(f"⚠️ Error enhancing image: {e}")
            return img
    
    def extract_percentages(self, text: str) -> List[float]:
        """Extract percentage values from OCR text."""
        try:
            # Find all percentage patterns
            pattern = r'(\d+(?:\.\d+)?)%'
            matches = re.findall(pattern, text)
            
            percentages = []
            for match in matches:
                try:
                    percentage = float(match)
                    if 0 <= percentage <= 100:  # Valid percentage range
                        percentages.append(percentage)
                except ValueError:
                    continue
            
            # Remove duplicates while preserving order
            seen = set()
            unique_percentages = []
            for p in percentages:
                if p not in seen:
                    seen.add(p)
                    unique_percentages.append(p)
            
            return unique_percentages
        except Exception as e:
            print(f"⚠️ Error extracting percentages: {e}")
            return []
    
    def start(self, initial_time: int = None):
        """Start the countdown timer."""
        if self.running:
            self.stop()
        
        if initial_time is not None:
            self.time_left = initial_time
            self.original_time = initial_time
        
        self.running = True
        self.notifications_sent.clear()
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        print(f"🎯 COCA timer started: {self.time_left//60}:{self.time_left%60:02d}")
    
    def stop(self):
        """Stop the timer."""
        self.running = False
        if self.timer_thread:
            self.timer_thread.join(timeout=1)
        print("⏹️ COCA timer stopped")
    
    def reset(self):
        """Reset the timer to original time."""
        was_running = self.running
        self.stop()
        self.time_left = self.original_time
        self.notifications_sent.clear()
        self.update_callback(self.time_left, "Reset")
        
        if was_running:
            self.start()
        
        print("🔄 COCA timer reset")
    
    def _timer_loop(self):
        """Main timer loop running in separate thread with smooth updates."""
        update_counter = 0

        while self.running and self.time_left > 0:
            # Update display every 100ms for smooth percentage counting
            self.update_callback(self.time_left, "Running")

            # Wait 100ms for smooth updates
            time.sleep(0.1)
            update_counter += 1

            # Decrease time only every 10 updates (every 1 second)
            if self.running and update_counter >= 10:
                self.time_left -= 1
                update_counter = 0

        # Timer finished
        if self.running:
            self.time_left = 0
            self.update_callback(self.time_left, "Completed!")
            print("🎉 COCA timer completed!")

        self.running = False
    
    # Audio methods removed for clean minimal implementation
