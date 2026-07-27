import { AppRegistry } from 'react-native';
import App from './App';
import './index.css';

// Register the app
AppRegistry.registerComponent('App', () => App);

// Run the app on the web
AppRegistry.runApplication('App', {
  initialProps: {},
  rootTag: document.getElementById('root'),
});
