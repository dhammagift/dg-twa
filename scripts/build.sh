#!/usr/bin/env bash
# Builds the TWA APK/AAB the same way CI does (.github/workflows/build-twa-release.yml):
# needs JDK 17, Android SDK (API 36 + build-tools 36.0.0, ANDROID_HOME/ANDROID_SDK_ROOT set)
# already installed — this script does not install them.
#
# Output is UNSIGNED (CI signs the APK afterwards via a separate GitHub Action using
# repo secrets KEYSTORE_BASE64/KEYSTORE_ALIAS/KEYSTORE_PASSWORD/KEY_PASSWORD, which
# don't exist locally) — sign app/build/outputs/apk/release/*-unsigned.apk yourself
# with apksigner before installing on a device that enforces signature verification.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

chmod +x gradlew
./gradlew build -x lint
./gradlew app:assembleRelease
./gradlew app:bundleRelease

echo "APK:  $REPO_ROOT/app/build/outputs/apk/release/"
echo "AAB:  $REPO_ROOT/app/build/outputs/bundle/release/app-release.aab"
