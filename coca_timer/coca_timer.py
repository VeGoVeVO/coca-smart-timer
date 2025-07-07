#!/usr/bin/env python3
"""
COCA Timer Core Module
Handles OCR percentage detection and countdown timer functionality.
"""

import threading
import time
import re
import os
from typing import Optional, List, Callable, Tuple
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2

# Handle both relative and absolute imports
try:
    from .debug_logger import debug_logger
except ImportError:
    from debug_logger import debug_logger

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
        Enhanced percentage detection with multiple OCR methods and debugging.

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

            # Save debug screenshot (only if debug logging is enabled)
            debug_logger.save_debug_screenshot(image, "original")

            # Convert to PIL Image with error handling
            pil_image = None
            try:
                if len(image.shape) == 3:
                    pil_image = Image.fromarray(image.astype('uint8'))
                else:
                    pil_image = Image.fromarray(image.astype('uint8')).convert('RGB')
                debug_logger.log_image_processing("PIL conversion", True, f"Size: {pil_image.size}")
            except Exception as e:
                debug_logger.log_image_processing("PIL conversion", False, str(e))
                return None

            # Use only the most accurate method for maximum speed
            methods = [
                ("Standard Enhanced", self._method_standard_enhanced)
            ]

            all_results = []

            for method_name, method_func in methods:

                try:
                    result = method_func(pil_image)
                    if result is not None:
                        all_results.append((method_name, result))

                    else:
                        pass
                except Exception as e:
                    print(f"⚠️ {method_name} failed: {e}")

            # Choose best result (prefer non-zero values)
            if all_results:
                # Filter out 0% results if we have other options
                non_zero_results = [(name, val) for name, val in all_results if val > 0]

                if non_zero_results:
                    # Use the first non-zero result
                    best_method, best_result = non_zero_results[0]
                else:
                    # Use the first result even if it's 0%
                    best_method, best_result = all_results[0]

                print(f"🔍 COCA OCR: Detected {best_result}% using {best_method}")
                debug_logger.log("INFO", f"� All results: {all_results}")
                return best_result
            else:
                debug_logger.log_final_result(None)
                return None

        except Exception as e:
            debug_logger.log("ERROR", f"⚠️ Critical OCR detection error: {e}")
            return None

    def _method_standard_enhanced(self, image: Image.Image) -> Optional[float]:
        """Fast standard enhanced OCR method."""
        try:
            enhanced = self.enhance_image_for_ocr(image)
            debug_logger.save_debug_screenshot(np.array(enhanced), "enhanced")

            # Only use the most effective PSM modes for speed
            configs = [
                '--psm 6 -c tessedit_char_whitelist=0123456789%',
                '--psm 8 -c tessedit_char_whitelist=0123456789%'
            ]

            for config in configs:
                text = pytesseract.image_to_string(enhanced, config=config)
                debug_logger.log_ocr_attempt("Standard Enhanced", config, text, '%' in text)

                percentages = self.extract_percentages(text)
                if percentages:
                    debug_logger.log_percentage_extraction(text, percentages, "Standard Enhanced")
                    return min(percentages)

            return None
        except Exception as e:
            debug_logger.log("ERROR", f"Standard Enhanced method failed: {e}")
            return None

    def _method_binary_threshold_specific(self, image: Image.Image, threshold: int) -> Optional[float]:
        """Binary threshold OCR method with specific threshold value for white text with black outlines."""
        try:
            debug_logger.log("DEBUG", f"🔬 Testing binary threshold: {threshold}")

            # Convert to grayscale
            gray = image.convert('L')

            # Apply specific binary threshold
            # For white text with black outlines, we want to keep white pixels (above threshold)
            binary = gray.point(lambda x: 255 if x > threshold else 0, mode='1')
            binary_rgb = binary.convert('RGB')

            debug_logger.save_debug_screenshot(np.array(binary_rgb), f"binary_{threshold}")

            # Try multiple PSM modes for better detection
            configs = [
                '--psm 6 -c tessedit_char_whitelist=0123456789%',
                '--psm 8 -c tessedit_char_whitelist=0123456789%',
                '--psm 7 -c tessedit_char_whitelist=0123456789%',
                '--psm 13 -c tessedit_char_whitelist=0123456789%'
            ]

            for config in configs:
                try:
                    text = pytesseract.image_to_string(binary_rgb, config=config)
                    debug_logger.log_ocr_attempt(f"Binary {threshold}", config, text, '%' in text)

                    percentages = self.extract_percentages(text)
                    if percentages:
                        debug_logger.log_percentage_extraction(text, percentages, f"Binary {threshold}")
                        return min(percentages)
                except Exception as e:
                    debug_logger.log("WARNING", f"OCR failed for Binary {threshold} with {config}: {e}")
                    continue

            return None
        except Exception as e:
            debug_logger.log("ERROR", f"Binary Threshold {threshold} method failed: {e}")
            return None



    def _method_high_contrast(self, image: Image.Image) -> Optional[float]:
        """Fast high contrast OCR method."""
        try:
            # Increase contrast dramatically
            contrast_enhancer = ImageEnhance.Contrast(image)
            high_contrast = contrast_enhancer.enhance(3.0)

            # Increase brightness
            brightness_enhancer = ImageEnhance.Brightness(high_contrast)
            bright = brightness_enhancer.enhance(1.5)

            debug_logger.save_debug_screenshot(np.array(bright), "high_contrast")

            # Only use the most effective PSM mode for speed
            text = pytesseract.image_to_string(bright, config='--psm 6 -c tessedit_char_whitelist=0123456789%')
            debug_logger.log_ocr_attempt("High Contrast", "--psm 6", text, '%' in text)

            percentages = self.extract_percentages(text)
            if percentages:
                debug_logger.log_percentage_extraction(text, percentages, "High Contrast")
                return min(percentages)

            return None
        except Exception as e:
            debug_logger.log("ERROR", f"High Contrast method failed: {e}")
            return None



    def _method_grayscale_sharpen(self, image: Image.Image) -> Optional[float]:
        """Grayscale with sharpening OCR method."""
        try:
            # Convert to grayscale
            gray = image.convert('L')

            # Apply sharpening filter
            sharpened = gray.filter(ImageFilter.SHARPEN)

            # Convert back to RGB for OCR
            rgb = sharpened.convert('RGB')

            debug_logger.save_debug_screenshot(np.array(rgb), "grayscale_sharp")

            configs = [
                '--psm 6 -c tessedit_char_whitelist=0123456789%',
                '--psm 8 -c tessedit_char_whitelist=0123456789%'
            ]

            for config in configs:
                text = pytesseract.image_to_string(rgb, config=config)
                debug_logger.log_ocr_attempt("Grayscale + Sharpen", config, text, '%' in text)

                percentages = self.extract_percentages(text)
                if percentages:
                    debug_logger.log_percentage_extraction(text, percentages, "Grayscale + Sharpen")
                    return min(percentages)

            return None
        except Exception as e:
            debug_logger.log("ERROR", f"Grayscale + Sharpen method failed: {e}")
            return None

    def _method_morphological(self, image: Image.Image) -> Optional[float]:
        """Morphological operations OCR method."""
        try:
            # Convert PIL to OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # Apply morphological operations
            kernel = np.ones((2, 2), np.uint8)
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

            # Convert back to PIL
            morph_pil = Image.fromarray(morph).convert('RGB')

            debug_logger.save_debug_screenshot(np.array(morph_pil), "morphological")

            configs = [
                '--psm 6 -c tessedit_char_whitelist=0123456789%',
                '--psm 8 -c tessedit_char_whitelist=0123456789%'
            ]

            for config in configs:
                text = pytesseract.image_to_string(morph_pil, config=config)
                debug_logger.log_ocr_attempt("Morphological", config, text, '%' in text)

                percentages = self.extract_percentages(text)
                if percentages:
                    debug_logger.log_percentage_extraction(text, percentages, "Morphological")
                    return min(percentages)

            return None
        except Exception as e:
            debug_logger.log("ERROR", f"Morphological method failed: {e}")
            return None

    def _method_multi_scale(self, image: Image.Image) -> Optional[float]:
        """Multi-scale OCR method."""
        try:
            scales = [1.5, 2.0, 2.5]

            for scale in scales:
                # Scale up the image
                new_size = (int(image.width * scale), int(image.height * scale))
                scaled = image.resize(new_size, Image.LANCZOS)

                # Apply enhancement
                enhanced = self.enhance_image_for_ocr(scaled)

                debug_logger.save_debug_screenshot(np.array(enhanced), f"multi_scale_{scale}")

                configs = [
                    '--psm 6 -c tessedit_char_whitelist=0123456789%',
                    '--psm 8 -c tessedit_char_whitelist=0123456789%'
                ]

                for config in configs:
                    text = pytesseract.image_to_string(enhanced, config=config)
                    debug_logger.log_ocr_attempt(f"Multi-Scale {scale}x", config, text, '%' in text)

                    percentages = self.extract_percentages(text)
                    if percentages:
                        debug_logger.log_percentage_extraction(text, percentages, f"Multi-Scale {scale}x")
                        return min(percentages)

            return None
        except Exception as e:
            debug_logger.log("ERROR", f"Multi-Scale method failed: {e}")
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
