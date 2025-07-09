# 🌿 COCA Smart Timer

A smart overlay timer for gaming with multi-stage plant lifecycle simulation, auto crop detection, and coca leaf-themed UI.

![COCA Smart Timer](assets/coca_logo.png)

## ✨ Features

### 🌱 **Multi-Stage Plant Lifecycle**
- **Growing Stage**: Initial timer with percentage progression
- **Ready Stage**: 4min (Cannabis) / 7.5min (Coca) preparation phase
- **Flowering Stage**: Cannabis (3.5min basic/3min box), Coca (8min basic/7.5min box)
- **Seeding Stage**: Infinite duration with ∞ symbol

### 🔍 **Auto Crop Detection**
- **Smart OCR**: Automatically detects "Coca" or "Cannabis" from screenshots
- **Dynamic Switching**: Overrides manual settings when crop type is detected
- **Fallback Mode**: Uses manual preferences when detection fails

### 🎮 **Gaming Features**
- **Floating Overlay**: Stays on top during gameplay with dynamic status display
- **Stage-Specific Colors**: Visual feedback for each growth phase
- **Real-Time Updates**: Live percentage counting and smooth animations
- **Customizable Triggers**: Set your own keyboard trigger words (2-10 characters)

### 🎨 **Modern UI**
- **Coca Leaf Theme**: Beautiful nature-inspired green design
- **Toggle Switches**: Modern preferences with intuitive controls
- **Clean Layout**: No clutter, proper text sizing and positioning
- **6 Overlay Positions**: Center top, corners, and more

## 🚀 Quick Start

> **⚠️ IMPORTANT**: Make sure your game is in **Windowed Mode** to see the timer overlay!

1. **Download** the latest release from [Releases](../../releases)
2. **Extract** `Smart-Coca-Timer.zip` to your desired location
3. **Run** `COCA-Smart-Timer.exe` from the extracted folder
4. **Configure** by right-clicking the system tray icon

## 🎮 How to Use

### Initial Setup
1. Launch the application
2. Use your trigger word (default: `ccc`) to start area selection
3. Select the area of your screen where percentages appear
4. Configure preferences (crop type, planter type, auto-detection)

### Plant Lifecycle
1. **Growing**: Timer counts down while percentage increases
2. **Ready**: Preparation phase after growing completes
3. **Flowering**: Production phase with stage-specific timing
4. **Seeding**: Infinite stage showing ∞ symbol

### Default Controls
- **Start Timer**: Type `ccc` (customizable)
- **Reset Area**: Type `rrr` (customizable)

### Customization
Right-click the system tray icon to access:
- **Growing Preferences**: Crop type, planter type, auto-detection
- **Orientation**: Choose overlay position (6 options)
- **Trigger Words**: Customize keyboard triggers
- **Exit**: Close the application

## 🎯 How It Works

### OCR & Detection
1. **Area Selection**: Select the screen region containing percentage values
2. **Dual Detection**: Simultaneously detects percentages AND crop type text
3. **Auto Switching**: Changes timer type based on detected "Coca" or "Cannabis"
4. **Smart Calculation**: Calculates time based on crop type and planter configuration

### Multi-Stage System
1. **Growing Phase**: Standard timer with percentage progression (19-38 min)
2. **Ready Phase**: Preparation time (4-7.5 min depending on crop)
3. **Flowering Phase**: Production time (3-8 min depending on crop/planter)
4. **Seeding Phase**: Infinite duration for collection

### Visual Feedback
- **Growing**: Light grey overlay with percentage counting
- **Ready**: Blue background (preparation phase)
- **Flowering**: Purple background (production phase)
- **Seeding**: Green background with ∞ symbol
- **Warnings**: Orange (5min) → Red (1min) → Completion sound

## ⏱️ Timer Configurations

### Crop Types & Timing
| Crop Type | Growing Time | Ready Time | Flowering Time (Basic) | Flowering Time (Box) |
|-----------|--------------|------------|----------------------|---------------------|
| **Coca** | 38 minutes | 7.5 minutes | 8 minutes | 7.5 minutes |
| **Cannabis** | 19 minutes | 4 minutes | 3.5 minutes | 3 minutes |

### Auto-Detection Keywords
- **Coca**: Detects "coca" (case-insensitive)
- **Cannabis**: Detects "cannabis" (case-insensitive)
- **Fallback**: Uses manual preference if no keyword detected

## 🔧 Technical Details

### Requirements
- **OS**: Windows 10/11
- **Python**: 3.8+ (bundled in executable)
- **OCR**: Tesseract OCR (bundled - no installation required!)
- **⚠️ IMPORTANT**: Game must be in **Windowed Mode** to see the timer overlay

### Built With
- **PyQt6**: Modern UI framework with custom toggle switches
- **Tesseract**: Enhanced OCR engine for text and crop recognition
- **MSS**: Fast screenshot capture
- **OpenCV**: Image processing and enhancement
- **Pynput**: Keyboard input detection

## 🎨 Design Philosophy

The application features a beautiful coca leaf-inspired design:
- **Colors**: Natural greens with stage-specific accents
- **Sounds**: Nature-inspired completion melodies
- **UI**: Modern rounded corners, smooth animations, and clean typography
- **UX**: Intuitive toggle switches and contextual visual feedback

## 📋 Configuration Options

### Trigger Words
- **Length**: 2-10 characters
- **Content**: Letters only (a-z)
- **Conflicts**: Cannot overlap with other triggers
- **Examples**: `coca`, `start`, `go`, `reset`

### Preferences
- **Auto Crop Detection**: Toggle automatic crop type detection
- **Manual Crop Type**: Choose Coca or Cannabis manually
- **Planter Type**: Select Basic Planter or Planter Box
- **Overlay Position**: 6 positioning options

## 🔊 Audio System

### Stage Notifications
- **5 Minutes Warning**: Single beep (800Hz) + orange flashing
- **1 Minute Warning**: Double beep (800Hz) + red flashing
- **Stage Completion**: Nature-inspired 3-tone melody (A4→C5→E5)

### Multi-Stage Audio
- **Growing Complete**: Completion sound → Ready stage begins
- **Ready Complete**: Completion sound → Flowering stage begins
- **Flowering Complete**: Completion sound → Seeding stage begins

## 🐛 Troubleshooting

### Common Issues
1. **OCR not detecting crop**: Ensure crop name is visible in selected area
2. **Auto-detection not working**: Check for "coca" or "cannabis" text in screenshot
3. **Triggers not detected**: Check for conflicting applications
4. **Overlay not visible**: Try different position from tray menu
5. **Preferences not saving**: Check file permissions in application folder

### Debug Features
- **Console Output**: Shows detection results and timer status
- **Config File**: Settings saved to `coca_config.json`
- **Error Logging**: Detailed error messages for troubleshooting

### Support
- Check the [Issues](../../issues) page for known problems
- Create a new issue with detailed description and screenshots
- Include console output for technical issues

## 🆕 What's New in v1.0.3

### 🌟 Major Features
- **Multi-Stage Plant Lifecycle**: Complete growth simulation system
- **Auto Crop Detection**: Intelligent OCR-based crop identification
- **Enhanced Preferences**: Modern UI with toggle switches

### 🎨 UI Improvements
- **Dynamic Status Display**: Shows current growth stage
- **Stage-Specific Colors**: Visual feedback for each phase
- **Fixed Text Issues**: No more cropping or positioning problems

### 🔊 Audio Fixes
- **Restored Sounds**: Completion sounds work for all stages
- **Better Timing**: Proper warning notifications
- **Stage Transitions**: Audio feedback for phase changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tesseract OCR Team**: Excellent text recognition engine
- **PyQt Team**: Robust UI framework with modern capabilities
- **Gaming Community**: Inspiration, feedback, and feature requests
- **PerpHeads Community**: Primary testing and use case development

---

**🎮 Built for PerpHeads Gmod Community**

*Experience the complete plant lifecycle with intelligent automation!*
