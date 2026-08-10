import { StyleSheet, Platform, StatusBar } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F0F2F5', // Light grey background for spacing
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  header: {
    height: 60,
    backgroundColor: '#FFFFFF',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E9EDEF',
  },
  headerButton: {
    padding: 10,
  },
  headerTitleContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 4,
  },
  smallAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginRight: 10,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#E9EDEF',
    resizeMode: 'contain',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '500',
    color: '#111B21',
  },
  scrollContent: {
    flex: 1,
  },
  sectionCard: {
    backgroundColor: '#FFFFFF',
    marginTop: 8,
    paddingVertical: 4,
  },
  heroContainer: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  heroAvatar: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#E9EDEF',
    resizeMode: 'contain',
  },
  heroNameContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
  },
  heroName: {
    fontSize: 22,
    fontWeight: '400',
    color: '#111B21',
    textAlign: 'center',
  },
  heroPhone: {
    fontSize: 16,
    color: '#667781',
    marginTop: 4,
  },
  shareButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#F0F2F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
  },
  shareText: {
    fontSize: 14,
    color: '#111B21',
    marginTop: 8,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  listIcon: {
    marginRight: 24,
  },
  listContent: {
    flex: 1,
    justifyContent: 'center',
  },
  listTextPrimary: {
    fontSize: 16,
    color: '#111B21',
    lineHeight: 22,
  },
  listTextSecondary: {
    fontSize: 14,
    color: '#667781',
    marginTop: 2,
    lineHeight: 20,
  },
  listTextLink: {
    fontSize: 16,
    color: '#027EB5', // Light mode link color
  },
  sectionHeader: {
    fontSize: 14,
    color: '#667781',
    marginLeft: 20,
    marginTop: 16,
    marginBottom: 4,
    fontWeight: '500',
  },
  greenCircleIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#00A884',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  }
});
