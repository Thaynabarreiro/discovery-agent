#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LAUNCHER_DIR="$PROJECT_DIR/macos/DiscoveryAgentLauncher"
APP_NAME="Discovery Agent Launcher"
APP_PATH="$HOME/Applications/$APP_NAME.app"
BUILD_DIR="$LAUNCHER_DIR/.build/release"
EXECUTABLE="$BUILD_DIR/$APP_NAME"

cd "$LAUNCHER_DIR"
swift build -c release

rm -rf "$APP_PATH"
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"
cp "$EXECUTABLE" "$APP_PATH/Contents/MacOS/$APP_NAME"

/usr/libexec/PlistBuddy -c "Clear dict" "$APP_PATH/Contents/Info.plist" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :CFBundleName string $APP_NAME" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string $APP_NAME" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string com.discovery-agent.launcher" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleVersion string 1.0" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string 1.0" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleExecutable string $APP_NAME" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundlePackageType string APPL" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :LSMinimumSystemVersion string 14.0" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :NSPrincipalClass string NSApplication" "$APP_PATH/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :NSHighResolutionCapable bool true" "$APP_PATH/Contents/Info.plist"

codesign --force --deep --sign - "$APP_PATH" >/dev/null
echo "Built $APP_PATH"
