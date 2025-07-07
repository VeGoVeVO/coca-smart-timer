#!/usr/bin/env python3
"""
Area Selector for COCA Timer
Tkinter-based screen area selection for OCR region configuration.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Tuple, Callable
import numpy as np
from PIL import Image, ImageTk
import threading


class AreaSelector:
    """Tkinter-based area selector for choosing OCR regions."""
    
    def __init__(self, screenshot: np.ndarray, 
                 on_area_selected: Callable[[Tuple[int, int, int, int]], None],
                 on_cancelled: Callable[[], None]):
        """
        Initialize area selector.
        
        Args:
            screenshot: Full screen screenshot as numpy array
            on_area_selected: Callback for when area is selected (x, y, width, height)
            on_cancelled: Callback for when selection is cancelled
        """
        self.screenshot = screenshot
        self.on_area_selected = on_area_selected
        self.on_cancelled = on_cancelled
        
        # Selection state
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selecting = False
        
        # UI components
        self.root = None
        self.canvas = None
        self.photo = None
        self.selection_rect = None
        
        # Don't setup UI in __init__, do it when show() is called
        self.root = None

        # Set display dimensions from screenshot
        if screenshot is not None:
            self.display_height, self.display_width = screenshot.shape[:2]
        else:
            # Fallback dimensions
            self.display_width = 1920
            self.display_height = 1080
    
    def setup_ui(self):
        """Setup the area selector UI."""
        # Create main window (not Toplevel to avoid blank window issue)
        self.root = tk.Tk()
        self.root.title("COCA Area Selector")

        # Hide from taskbar and make it invisible initially
        self.root.withdraw()
        self.root.attributes('-toolwindow', True)  # Hide from taskbar on Windows
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')

        # Remove window decorations completely
        self.root.overrideredirect(True)
        
        # Handle escape key
        self.root.bind('<Escape>', self.cancel_selection)
        self.root.focus_set()
        
        # Convert screenshot to PhotoImage
        self.convert_screenshot()

        # Set window geometry to cover entire screen
        self.root.geometry(f"{self.display_width}x{self.display_height}+0+0")

        # Create canvas
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Display screenshot
        if self.photo:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.start_selection)
        self.canvas.bind('<B1-Motion>', self.update_selection)
        self.canvas.bind('<ButtonRelease-1>', self.end_selection)
        
        # Add instructions
        self.add_instructions()
    
    def convert_screenshot(self):
        """Convert numpy screenshot to PhotoImage."""
        try:
            # Convert to PIL Image
            if len(self.screenshot.shape) == 3:
                pil_image = Image.fromarray(self.screenshot.astype('uint8'))
            else:
                pil_image = Image.fromarray(self.screenshot.astype('uint8')).convert('RGB')
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(pil_image)
            print(f"✅ Screenshot converted for display: {pil_image.size}")
            
        except Exception as e:
            print(f"⚠️ Error converting screenshot: {e}")
            self.photo = None
    
    def add_instructions(self):
        """Add instruction text to the canvas."""
        instructions = [
            "COCA Area Selection",
            "",
            "Click and drag to select the area containing percentage values",
            "Press ESC to cancel",
            "Release mouse to confirm selection"
        ]
        
        # Create semi-transparent background
        text_bg = self.canvas.create_rectangle(
            20, 20, 400, 120,
            fill='black', stipple='gray50', outline='white'
        )
        
        # Add instruction text
        y_offset = 30
        for line in instructions:
            self.canvas.create_text(
                30, y_offset,
                text=line,
                fill='white',
                font=('Arial', 12, 'bold' if line == instructions[0] else 'normal'),
                anchor=tk.NW
            )
            y_offset += 18
    
    def start_selection(self, event):
        """Start area selection."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.selecting = True
        
        # Remove previous selection rectangle
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        print(f"🎯 Selection started at ({self.start_x}, {self.start_y})")
    
    def update_selection(self, event):
        """Update selection rectangle during drag."""
        if not self.selecting:
            return
        
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        
        # Remove previous rectangle
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        # Draw new rectangle
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.end_x, self.end_y,
            outline='cyan', width=2, fill='cyan', stipple='gray25'
        )
        
        # Show selection info
        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)
        
        # Remove previous info text
        self.canvas.delete('selection_info')
        
        # Add selection info
        info_text = f"Selection: {int(width)} x {int(height)}"
        self.canvas.create_text(
            self.end_x + 10, self.end_y - 10,
            text=info_text,
            fill='yellow',
            font=('Arial', 10, 'bold'),
            anchor=tk.NW,
            tags='selection_info'
        )
    
    def end_selection(self, event):
        """End area selection and confirm."""
        if not self.selecting:
            return
        
        self.selecting = False
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        
        # Calculate selection area
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        width = int(x2 - x1)
        height = int(y2 - y1)
        
        # Validate selection size
        if width < 20 or height < 20:
            messagebox.showwarning("Invalid Selection", "Selected area is too small. Please select a larger area.")
            return
        
        # Create area tuple (x, y, width, height)
        selected_area = (int(x1), int(y1), width, height)
        
        print(f"✅ Area selected: {selected_area}")
        
        # Close window and call callback
        self.cleanup_and_close()
        self.on_area_selected(selected_area)
    
    def cancel_selection(self, event=None):
        """Cancel area selection."""
        print("❌ Area selection cancelled")
        self.cleanup_and_close()
        self.on_cancelled()

    def cleanup_and_close(self):
        """Properly cleanup and close the Tkinter window - simplified version."""
        try:
            if self.root:
                try:
                    self.root.quit()  # Exit mainloop
                    self.root.destroy()  # Destroy window
                    print("✅ Area selector window closed")
                except Exception as e:
                    print(f"⚠️ Error closing window: {e}")
                finally:
                    self.root = None

            # Clean up resources
            self.screenshot = None
            self.photo = None
            self.canvas = None
            self.selection_rect = None

        except Exception as e:
            print(f"⚠️ Error in cleanup: {e}")
            self.root = None
    
    def show(self):
        """Show the area selector window - simplified and working version."""
        try:
            # Don't setup UI in __init__, do it here when we're ready to show
            self.setup_ui()
            if self.root:
                # Show the window immediately - no threading
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
                self.root.attributes('-topmost', True)

                print("🎯 Area selector window opened - select the area")

                # Start mainloop directly - this will block until window closes
                self.root.mainloop()
            else:
                print("⚠️ Failed to create area selector window")
        except Exception as e:
            print(f"⚠️ Critical error showing area selector: {e}")
