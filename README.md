# WhatsApp App Simulation (Mobile)

This branch (`whatsapp-app-simulation`) contains a simulated WhatsApp chat application using **React Native** and **Expo**.

The simulation illustrates how rural patients, community healthcare workers (ASHAs), and physicians interact with the **Rural Healthcare AI Bot** on mobile devices.

## Tech Stack
- **React Native** (using standard native components like `View`, `Text`, `StyleSheet`, `ScrollView`, etc.)
- **Expo** (for fast development, easy testing via Expo Go, and building)
- **Lucide React Native** for high-quality, modern icons

## Project Structure
All application files reside in the `App/` directory:
- `App/package.json` — dependencies and scripts
- `App/app.json` — Expo configuration
- `App/App.js` — App entry point
- `App/src/` — Main source code directory
  - `/assets/` — Images, fonts, and static assets
  - `/components/` — Reusable React Native UI components
  - `/constants/` — Configurations, themes, and translations (e.g. `translations.js`)
  - `/context/` — React Context providers for global state
  - `/hooks/` — Custom React hooks
  - `/navigation/` — React Navigation setup
  - `/screens/` — Full-page UI screen components
  - `/services/` — API calls and external integrations
  - `/utils/` — Helper functions

## Getting Started

### Prerequisites
1. Make sure you have **Node.js** installed.
2. Install the **Expo Go** app on your physical iOS or Android device.

### Installation
From the root of the repository, navigate to the `App` directory and install the dependencies:
```bash
cd App
npm install
```

### Running Locally with Expo Go
To start the Expo development server:
```bash
npm start
```
or <br>
```bash
npx expo start
```
*This will open the Expo Developer Tools in your browser or terminal and print a QR code.*

### Testing on your Device
1. Open the **Expo Go** app on your phone.
2. Scan the QR code displayed in your terminal (using the Expo Go app on Android, or the default Camera app on iOS).
3. The app will automatically bundle and launch on your phone!

### Available Scripts
- `npm start` - Starts the Expo bundler.
- `npm run android` - Starts the bundler and attempts to open the app on a connected Android emulator.
- `npm run ios` - Starts the bundler and attempts to open the app on an iOS simulator (Mac only).
