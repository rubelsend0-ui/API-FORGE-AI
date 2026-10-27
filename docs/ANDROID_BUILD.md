# Android Build

## Local build (Android Studio — recommended)

1. Open the `android/` folder as a project in Android Studio
   (Giraffe or newer).
2. Android Studio will detect there's no committed Gradle wrapper and
   offer to generate one — accept it. This creates `gradlew`,
   `gradlew.bat`, and `gradle/wrapper/gradle-wrapper.jar`.
3. Let Gradle sync, then Run on an emulator or device.
4. In the app's Settings screen, set the backend URL:
   - Android emulator talking to a backend on your host machine:
     `http://10.0.2.2:8000`
   - A real device on the same network: your machine's LAN IP, e.g.
     `http://192.168.1.20:8000`
   - A deployed backend: its real HTTPS URL.

## Local build (command line, if you have Gradle installed)

```bash
cd android
gradle wrapper --gradle-version 8.10.2 --distribution-type bin
git add gradlew gradlew.bat gradle/wrapper/gradle-wrapper.jar
./gradlew assembleDebug
```

The APK lands at `android/app/build/outputs/apk/debug/app-debug.apk`.

## GitHub Actions build

`.github/workflows/android-build.yml` builds the debug APK on every
push to `main`, every PR, and on manual dispatch. It does **not**
require a committed Gradle wrapper — it provisions Gradle directly via
`gradle/actions/setup-gradle`.

```bash
gh workflow run android-build.yml
gh run watch
gh run download --name api-forge-ai-debug-apk
```

## Known gaps

- Only 4 screens are implemented (Home, Import, Analysis, Settings) —
  the full spec describes 13. The rest (Project Details, Build Center,
  GitHub Connection, Render Deployment, API Tester, etc.) are not built.
- Settings (backend URL / API key) are kept in memory only and reset
  when the app restarts — DataStore is already a dependency for when
  persistence is added.
- No automated Android tests yet.
