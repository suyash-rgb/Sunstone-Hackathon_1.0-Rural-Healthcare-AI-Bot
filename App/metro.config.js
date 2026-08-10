const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Add .mjs to the source extensions so Metro can resolve lucide-react-native .mjs files
config.resolver.sourceExts.push('mjs');

module.exports = config;
