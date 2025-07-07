# 🌿 COCA Smart Timer

A smart overlay timer for gaming with OCR percentage detection and coca leaf-themed UI.

![COCA Smart Timer](assets/coca_logo.png)

## ✨ Features

- 🎯 **Smart OCR Detection**: Automatically detects percentages from your screen
- ⏱️ **Intelligent Timer**: Calculates remaining time based on detected percentage
- 🎮 **Gaming-Friendly**: Floating overlay that stays on top during gameplay
- 🔧 **Customizable Triggers**: Set your own keyboard trigger words (2-10 characters)
- 🎨 **Coca Leaf Theme**: Beautiful nature-inspired green UI design
- 🔊 **Nature Sounds**: Gentle completion melody that fits the theme
- 📍 **Flexible Positioning**: 6 overlay positions (center top, corners, etc.)
- 💾 **Persistent Settings**: Remembers your preferences between sessions

## 🚀 Quick Start

1. **Download** the latest release from [Releases](../../releases)
2. **Extract** the ZIP file to your desired location
3. **Run** `COCA-Smart-Timer.exe`
4. **Configure** by right-clicking the system tray icon

## 🎮 How to Use

### Initial Setup
1. Launch the application
2. Use your trigger word (default: `ccc`) to start area selection
3. Select the area of your screen where percentages appear
4. The timer will automatically detect percentages and start counting

### Default Controls
- **Start Timer**: Type `ccc` (customizable)
- **Reset Area**: Type `rrr` (customizable)

### Customization
Right-click the system tray icon to access:
- **Orientation**: Choose overlay position
- **Trigger Words**: Customize your keyboard triggers
- **Exit**: Close the application

## 🎯 How It Works

1. **Area Selection**: Select the screen region containing percentage values
2. **OCR Detection**: Uses Tesseract OCR to detect percentage numbers
3. **Smart Calculation**: Calculates remaining time based on 38-minute total duration
4. **Visual Feedback**: 
   - Normal: Light grey overlay
   - 5 minutes: Orange-yellow warning
   - 1 minute: Red alert
   - Completion: Nature-inspired sound

## 🔧 Technical Details

### Requirements
- **OS**: Windows 10/11
- **Python**: 3.8+ (bundled in executable)
- **OCR**: Tesseract OCR (auto-installed)

### Built With
- **PyQt6**: Modern UI framework
- **Tesseract**: OCR engine for text recognition
- **MSS**: Fast screenshot capture
- **OpenCV**: Image processing
- **Pynput**: Keyboard input detection

## 🎨 Coca Leaf Theme

The application features a beautiful coca leaf-inspired design:
- **Colors**: Natural greens and earth tones
- **Sounds**: Wind-through-leaves completion melody
- **UI**: Organic rounded corners and gradients

## 📋 Validation Rules

### Trigger Words
- **Length**: 2-10 characters
- **Content**: Letters only (a-z)
- **Conflicts**: Cannot overlap with other triggers
- **Examples**: `coca`, `start`, `go`, `reset`

## 🔊 Audio Feedback

- **5 Minutes**: Single beep (800Hz)
- **1 Minute**: Double beep (800Hz)
- **Completion**: Nature-inspired 3-tone melody (A4→C5→E5)

## 🐛 Troubleshooting

### Common Issues
1. **OCR not working**: Ensure good contrast in selected area
2. **Triggers not detected**: Check for conflicting applications
3. **Overlay not visible**: Try different position from tray menu

### Support
- Check the [Issues](../../issues) page
- Create a new issue with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Tesseract OCR team for excellent text recognition
- PyQt team for the robust UI framework
- Gaming community for inspiration and feedback

---

**Built for PerpHeads Gmod community**
