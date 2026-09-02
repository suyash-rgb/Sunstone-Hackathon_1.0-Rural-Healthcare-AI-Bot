import { Linking, Platform, Alert } from 'react-native';

/**
 * Opens navigation directions to the specified latitude and longitude in Google Maps or Apple Maps.
 * @param {Object} params
 * @param {number} params.latitude
 * @param {number} params.longitude
 * @param {string} [params.label]
 */
export const openDirectionsInMaps = async ({ latitude, longitude, label = 'Hospital' }) => {
  const destination = `${latitude},${longitude}`;
  const encodedLabel = encodeURIComponent(label);

  const androidUri = `google.navigation:q=${destination}&mode=d`;
  const iosGoogleMapsUri = `comgooglemaps://?daddr=${destination}&directionsmode=driving`;
  const appleMapsUri = `maps:0,0?q=${encodedLabel}&daddr=${destination}&dirflg=d`;
  const universalWebUri = `https://www.google.com/maps/dir/?api=1&destination=${destination}`;

  try {
    if (Platform.OS === 'android') {
      const canOpen = await Linking.canOpenURL(androidUri);
      if (canOpen) {
        await Linking.openURL(androidUri);
      } else {
        await Linking.openURL(universalWebUri);
      }
    } else if (Platform.OS === 'ios') {
      const canOpenGoogle = await Linking.canOpenURL(iosGoogleMapsUri);
      if (canOpenGoogle) {
        await Linking.openURL(iosGoogleMapsUri);
      } else {
        await Linking.openURL(appleMapsUri);
      }
    } else {
      await Linking.openURL(universalWebUri);
    }
  } catch (error) {
    console.error("Navigation error:", error);
    Alert.alert('Navigation Error', 'Unable to open maps application.');
  }
};
