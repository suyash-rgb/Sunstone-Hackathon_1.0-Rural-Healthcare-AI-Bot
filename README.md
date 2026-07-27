# WhatsApp App Simulation

This branch (`whatsapp-app-simulation`) contains a simulated WhatsApp chat application using React Native Web and Vite.

The simulation illustrates how rural patients, community healthcare workers (ASHAs), and physicians interact with the **Rural Healthcare AI Bot**.

## Tech Stack
- **React 18**
- **React Native Web** (using standard native components like `View`, `Text`, `StyleSheet`, `ScrollView`, etc., rendered on the web)
- **Vite** for building and dev tooling (aliased to serve React Native components on the web)
- **Lucide React** for high-quality, modern icons

## Project Structure
All application files reside in the `App/` directory:
- `App/package.json` — dependencies and scripts
- `App/vite.config.js` — bundler configuration mapping `react-native` imports to `react-native-web`
- `App/index.html` — HTML root
- `App/src/index.jsx` — app registry entrypoint
- `App/src/App.jsx` — main dashboard and layout
- `App/src/mockData.js` — simulation chat rooms and conversational responses

## Getting Started

### Prerequisites
Make sure you have Node.js installed.

### Installation
From the root of the repository, navigate to the `App` directory and install the dependencies:
```bash
cd App
npm install
```

### Running Locally
To start the Vite development server:
```bash
npm run dev
```

### Building for Production
To build the static application bundle (emits files to `App/dist/`):
```bash
npm run build
```
