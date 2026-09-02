import React from 'react';
import { View, Text, Image, TouchableOpacity, Pressable } from 'react-native';
import { Navigation } from 'lucide-react-native';
import { openDirectionsInMaps } from '../utils/navigation';
import { hospitalCardStyles as styles } from '../constants/styles';

export const HospitalCard = ({ hospital }) => {
  const handleNavigate = () => {
    openDirectionsInMaps({
      latitude: hospital.lat,
      longitude: hospital.lon,
      label: hospital.name,
    });
  };

  const distanceKm = typeof hospital.distance_meters === 'number' 
    ? (hospital.distance_meters / 1000).toFixed(1) 
    : hospital.distance_km || '1.5';
    
  const isEmergency = hospital.emergency === 'yes' || hospital.emergency === '24/7 Trauma';

  return (
    <View style={styles.card}>
      <Pressable onPress={handleNavigate} style={styles.previewContainer}>
        <Image
          source={{
            uri: hospital.image || 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=400&h=200&q=80',
          }}
          style={styles.mapImage}
          resizeMode="cover"
        />
        <View style={[styles.badge, isEmergency ? styles.badgeTrauma : styles.badgeFacility]}>
          <Text style={styles.badgeText}>
            {isEmergency ? '24/7 TRAUMA' : (hospital.badge || 'CHC FACILITY')}
          </Text>
        </View>
      </Pressable>

      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={1}>
          {hospital.name}
        </Text>
        <Text style={styles.subtitle}>
          {hospital.tier || 'Medical Centre'} • {distanceKm} km away
        </Text>
        {hospital.services ? (
          <Text style={styles.services} numberOfLines={1}>
            {hospital.services}
          </Text>
        ) : null}

        <TouchableOpacity style={styles.actionButton} onPress={handleNavigate} activeOpacity={0.8}>
          <Navigation size={15} color="#FFFFFF" style={{ marginRight: 6 }} />
          <Text style={styles.buttonText}>Navigate in Maps</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};
