import { StyleSheet, Platform, StatusBar } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#075E54', // Matches iOS status bar area
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    height: 60,
    backgroundColor: '#075E54',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    justifyContent: 'space-between',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    zIndex: 10,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  backButton: {
    padding: 4,
    marginRight: 4,
  },
  avatarImage: {
    width: 40,
    height: 40,
    borderRadius: 20,
    marginRight: 10,
    backgroundColor: '#fff',
  },
  headerTitleContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  headerName: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 18,
  },
  headerStatus: {
    color: '#ffffff',
    fontSize: 13,
    opacity: 0.8,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconButton: {
    padding: 10,
    marginLeft: 4,
  },
  chatAreaWrapper: {
    flex: 1,
    position: 'relative',
  },
  chatBackground: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: '#E5DDD5', // WhatsApp classic light background
  },
  messageArea: {
    flex: 1,
  },
  messageAreaContent: {
    paddingHorizontal: 12,
    paddingVertical: 16,
    paddingBottom: 20,
  },
  msgRow: {
    flexDirection: 'row',
    marginVertical: 4,
    width: '100%',
  },
  msgRowLeft: {
    justifyContent: 'flex-start',
  },
  msgRowRight: {
    justifyContent: 'flex-end',
  },
  bubble: {
    maxWidth: '80%',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 6,
    position: 'relative',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1,
    elevation: 1,
  },
  bubbleMe: {
    backgroundColor: '#DCF8C6',
    borderTopRightRadius: 0,
  },
  bubbleOther: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 0,
  },
  bubbleText: {
    color: '#000000',
    fontSize: 15,
    lineHeight: 20,
  },
  bubbleFooter: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    marginTop: 2,
  },
  bubbleTime: {
    color: '#8696a0',
    fontSize: 11,
    marginRight: 4,
  },
  checkIcon: {
    marginLeft: 2,
  },
  typingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  typingText: {
    color: '#8696a0',
    fontSize: 14,
    marginLeft: 8,
    fontStyle: 'italic',
  },
  bubbleImage: {
    width: 240,
    height: 240,
    borderRadius: 8,
    marginBottom: 4,
  },
  documentContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.05)',
    padding: 8,
    borderRadius: 8,
    marginBottom: 4,
  },
  documentIconBox: {
    width: 40,
    height: 40,
    backgroundColor: '#FF5722',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  documentName: {
    flex: 1,
    fontSize: 14,
    color: '#111B21',
    fontWeight: '500'
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 8,
    paddingVertical: 8,
    backgroundColor: '#E5DDD5', // Match chat background to look transparent
  },
  inputContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    minHeight: 48,
    marginRight: 8,
    paddingHorizontal: 4,
  },
  inputIconButton: {
    padding: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  chatTextInput: {
    flex: 1,
    fontSize: 16,
    color: '#000',
    paddingTop: 12,
    paddingBottom: 12,
    maxHeight: 120,
  },
  micButton: {
    justifyContent: 'flex-end',
    paddingBottom: 2,
  },
  micCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#075E54', // WhatsApp Green Button
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 2,
  },
});
