# Changelog

All notable changes to COCA Smart Timer will be documented in this file.

## [v1.0.3] - 2025-01-09

### 🌟 Major New Features
- **Multi-Stage Plant Lifecycle System**: Complete plant growth simulation with 4 stages
  - Growing → Ready → Flowering → Seeding
  - Each stage has its own timer and visual indicators
  - Automatic progression through all growth phases
- **Auto Crop Type Detection**: Intelligent OCR-based crop identification
  - Automatically detects "Coca" or "Cannabis" from screenshots
  - Overrides manual settings when detection is successful
  - Fallback to manual settings when detection fails
- **Enhanced Preferences Dialog**: Complete redesign with modern UI
  - Custom toggle switch for auto-detection (replaces buggy checkbox)
  - Clean layout without information clutter
  - Proper text sizing and element positioning

### 🎨 UI/UX Improvements
- **Dynamic Status Display**: Shows current growth stage in overlay
  - "Growing" → "Ready" → "Flowering" → "Seeding"
  - Infinity symbol (∞) for seeding stage
- **Stage-Specific Colors**: Visual feedback for each growth phase
  - Growing: Light grey background
  - Ready: Blue background  
  - Flowering: Purple background
  - Seeding: Green background
- **Improved Floating UI**: Now shows crop type dynamically
  - "Coca: MM:SS | XX.XX % | Status" format
  - Updates based on auto-detection results

### ⏱️ Timer System Enhancements
- **Ready Stage Timing**:
  - Cannabis: 4 minutes (all planters)
  - Coca: 7.5 minutes (all planters)
- **Flowering Stage Timing**:
  - Cannabis Basic: 3.5 minutes
  - Cannabis Planter Box: 3 minutes
  - Coca Basic: 8 minutes
  - Coca Planter Box: 7.5 minutes
- **Seeding Stage**: Infinite duration with ∞ symbol

### 🐛 Bug Fixes
- **Fixed Flashing Behavior**: Stages no longer flash from start
  - Only flash during warning periods (5min/1min)
  - Proper reset when transitioning between stages
- **Preferences Dialog Issues**:
  - Fixed save button not working properly
  - Removed text cropping issues
  - Fixed checkbox interaction problems
- **Config File Management**: Ensures settings save to correct location
- **Initial Status Display**: Shows "---" instead of "Ready" when not started

### 🔧 Technical Improvements
- **Enhanced OCR Detection**: Improved text extraction for crop identification
- **Better Error Handling**: More robust error recovery in all systems
- **Optimized Performance**: Smoother animations and transitions
- **Code Cleanup**: Removed redundant code and improved maintainability

### 📝 Detection Keywords
- **Coca Detection**: Looks for "coca" (case-insensitive)
- **Cannabis Detection**: Looks for "cannabis" only (no alternatives)

---

## [v1.0.2] - Previous Release
- Basic timer functionality
- OCR percentage detection
- Simple preferences system

## [v1.0.1] - Previous Release  
- Initial release
- Core timer features
- Basic UI implementation
