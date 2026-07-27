import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Dimensions,
  ActivityIndicator
} from 'react-native';
import {
  Search,
  Send,
  MoreVertical,
  Phone,
  Video,
  Paperclip,
  Smile,
  CheckCheck,
  Bot,
  User,
  ArrowLeft,
  MessageSquare
} from 'lucide-react';
import { initialChats, getSimulatedResponse } from './mockData';

export default function App() {
  const [chats, setChats] = useState(initialChats);
  const [activeChatId, setActiveChatId] = useState('ai-bot');
  const [inputText, setInputText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isMobile, setIsMobile] = useState(Dimensions.get('window').width < 768);
  const [showSidebarOnMobile, setShowSidebarOnMobile] = useState(true);

  const scrollViewRef = useRef(null);

  // Responsive design checker
  useEffect(() => {
    const handleResize = () => {
      const width = Dimensions.get('window').width;
      const mobileStatus = width < 768;
      setIsMobile(mobileStatus);
      if (!mobileStatus) {
        setShowSidebarOnMobile(true);
      }
    };

    const subscription = Dimensions.addEventListener('change', handleResize);
    return () => {
      if (subscription?.remove) {
        subscription.remove();
      }
    };
  }, []);

  const activeChat = chats.find(c => c.id === activeChatId);

  // Auto scroll to bottom of chat
  useEffect(() => {
    if (scrollViewRef.current) {
      setTimeout(() => {
        scrollViewRef.current.scrollToEnd({ animated: true });
      }, 50);
    }
  }, [activeChat?.messages, isTyping]);

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    const messageText = inputText.trim();
    setInputText('');

    const newMsg = {
      id: `msg-${Date.now()}`,
      text: messageText,
      sender: 'me',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    // Update state with sent message
    setChats(prevChats =>
      prevChats.map(c => {
        if (c.id === activeChatId) {
          return {
            ...c,
            messages: [...c.messages, newMsg]
          };
        }
        return c;
      })
    );

    // Simulate Bot Response
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      const botReply = getSimulatedResponse(messageText, activeChat.name);
      const botMsg = {
        id: `msg-bot-${Date.now()}`,
        text: botReply,
        sender: 'other',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setChats(prevChats =>
        prevChats.map(c => {
          if (c.id === activeChatId) {
            return {
              ...c,
              messages: [...c.messages, botMsg]
            };
          }
          return c;
        })
      );
    }, 1200);
  };

  const selectChat = (id) => {
    setActiveChatId(id);
    if (isMobile) {
      setShowSidebarOnMobile(false);
    }
  };

  const filteredChats = chats.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.appWrapper}>
        {/* SIDEBAR PANEL */}
        {(!isMobile || showSidebarOnMobile) && (
          <View style={[styles.sidebar, isMobile && styles.mobileFullWidth]}>
            {/* Sidebar Header */}
            <View style={styles.header}>
              <View style={styles.profileArea}>
                <View style={styles.avatarCircle}>
                  <Text style={styles.avatarText}>👤</Text>
                </View>
                <Text style={styles.profileName}>Rural User</Text>
              </View>
              <View style={styles.headerIcons}>
                <TouchableOpacity style={styles.iconButton}>
                  <MessageSquare size={20} color="#8696a0" />
                </TouchableOpacity>
                <TouchableOpacity style={styles.iconButton}>
                  <MoreVertical size={20} color="#8696a0" />
                </TouchableOpacity>
              </View>
            </View>

            {/* Search Bar */}
            <View style={styles.searchContainer}>
              <View style={styles.searchInner}>
                <Search size={18} color="#8696a0" style={styles.searchIcon} />
                <TextInput
                  placeholder="Search or start new chat"
                  placeholderTextColor="#8696a0"
                  style={styles.searchInput}
                  value={searchQuery}
                  onChangeText={setSearchQuery}
                />
              </View>
            </View>

            {/* Chat List */}
            <ScrollView style={styles.chatList}>
              {filteredChats.map(item => {
                const isSelected = item.id === activeChatId;
                const lastMsg = item.messages[item.messages.length - 1];
                return (
                  <TouchableOpacity
                    key={item.id}
                    style={[styles.chatListItem, isSelected && styles.selectedItem]}
                    onPress={() => selectChat(item.id)}
                  >
                    <Text style={styles.chatAvatar}>{item.avatar}</Text>
                    <View style={styles.chatListItemContent}>
                      <View style={styles.chatListItemHeader}>
                        <Text style={styles.chatItemName}>{item.name}</Text>
                        <Text style={styles.chatItemTime}>{lastMsg ? lastMsg.time : ''}</Text>
                      </View>
                      <Text style={styles.chatItemText} numberOfLines={1}>
                        {lastMsg ? lastMsg.text : 'No messages yet'}
                      </Text>
                    </View>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          </View>
        )}

        {/* CHAT WINDOW PANEL */}
        {(!isMobile || !showSidebarOnMobile) && activeChat && (
          <View style={[styles.chatWindow, isMobile && styles.mobileFullWidth]}>
            {/* Chat Header */}
            <View style={styles.header}>
              {isMobile && (
                <TouchableOpacity
                  style={styles.backButton}
                  onPress={() => setShowSidebarOnMobile(true)}
                >
                  <ArrowLeft size={20} color="#8696a0" />
                </TouchableOpacity>
              )}
              <Text style={styles.activeChatAvatar}>{activeChat.avatar}</Text>
              <View style={styles.headerMeta}>
                <Text style={styles.activeChatName}>{activeChat.name}</Text>
                <Text style={styles.activeChatStatus}>
                  {isTyping ? 'typing...' : activeChat.status}
                </Text>
              </View>
              <View style={styles.headerIcons}>
                <TouchableOpacity style={styles.iconButton}>
                  <Video size={20} color="#8696a0" />
                </TouchableOpacity>
                <TouchableOpacity style={styles.iconButton}>
                  <Phone size={20} color="#8696a0" />
                </TouchableOpacity>
                <TouchableOpacity style={styles.iconButton}>
                  <MoreVertical size={20} color="#8696a0" />
                </TouchableOpacity>
              </View>
            </View>

            {/* Chat Messages */}
            <ScrollView
              ref={scrollViewRef}
              style={styles.messageArea}
              contentContainerStyle={styles.messageAreaContent}
            >
              {activeChat.messages.map(msg => {
                const isMe = msg.sender === 'me';
                return (
                  <View
                    key={msg.id}
                    style={[styles.msgRow, isMe ? styles.msgRowRight : styles.msgRowLeft]}
                  >
                    <View style={[styles.bubble, isMe ? styles.bubbleMe : styles.bubbleOther]}>
                      <Text style={styles.bubbleText}>{msg.text}</Text>
                      <View style={styles.bubbleFooter}>
                        <Text style={styles.bubbleTime}>{msg.time}</Text>
                        {isMe && <CheckCheck size={14} color="#53bdeb" style={styles.checkIcon} />}
                      </View>
                    </View>
                  </View>
                );
              })}

              {isTyping && (
                <View style={[styles.msgRow, styles.msgRowLeft]}>
                  <View style={[styles.bubble, styles.bubbleOther, styles.typingBubble]}>
                    <ActivityIndicator size="small" color="#00a884" />
                    <Text style={styles.typingText}>Typing response...</Text>
                  </View>
                </View>
              )}
            </ScrollView>

            {/* Chat Input Bar */}
            <View style={styles.inputBar}>
              <TouchableOpacity style={styles.inputIconButton}>
                <Smile size={24} color="#8696a0" />
              </TouchableOpacity>
              <TouchableOpacity style={styles.inputIconButton}>
                <Paperclip size={22} color="#8696a0" />
              </TouchableOpacity>

              <TextInput
                placeholder="Type a message"
                placeholderTextColor="#8696a0"
                style={styles.chatTextInput}
                value={inputText}
                onChangeText={setInputText}
                onSubmitEditing={handleSendMessage}
              />

              <TouchableOpacity style={styles.sendButton} onPress={handleSendMessage}>
                <Send size={20} color="#8696a0" />
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0c1317', // WhatsApp Darkest BG
  },
  appWrapper: {
    flex: 1,
    flexDirection: 'row',
    alignSelf: 'center',
    width: '100%',
    maxWidth: 1600,
    height: '100%',
    backgroundColor: '#111b21', // WhatsApp Panel BG
  },
  sidebar: {
    width: '30%',
    minWidth: 320,
    borderRightWidth: 1,
    borderColor: '#222d34',
    backgroundColor: '#111b21',
  },
  chatWindow: {
    flex: 1,
    backgroundColor: '#0b141a', // WhatsApp chat screen BG
  },
  mobileFullWidth: {
    width: '100%',
    flex: 1,
  },
  header: {
    height: 60,
    backgroundColor: '#202c33',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    justifyContent: 'space-between',
  },
  profileArea: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatarCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#2a3942',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    fontSize: 20,
  },
  profileName: {
    color: '#e9edef',
    fontWeight: 'bold',
    fontSize: 16,
  },
  headerIcons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconButton: {
    padding: 8,
    marginLeft: 8,
  },
  backButton: {
    marginRight: 8,
    padding: 4,
  },
  searchContainer: {
    padding: 8,
    backgroundColor: '#111b21',
    borderBottomWidth: 1,
    borderBottomColor: '#222d34',
  },
  searchInner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#202c33',
    borderRadius: 8,
    paddingHorizontal: 12,
    height: 36,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    color: '#e9edef',
    fontSize: 14,
    outlineStyle: 'none', // Remove web outline
  },
  chatList: {
    flex: 1,
  },
  chatListItem: {
    flexDirection: 'row',
    padding: 12,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#222d34',
  },
  selectedItem: {
    backgroundColor: '#2a3942',
  },
  chatAvatar: {
    fontSize: 28,
    marginRight: 12,
  },
  chatListItemContent: {
    flex: 1,
  },
  chatListItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  chatItemName: {
    color: '#e9edef',
    fontWeight: 'bold',
    fontSize: 15,
  },
  chatItemTime: {
    color: '#8696a0',
    fontSize: 12,
  },
  chatItemText: {
    color: '#8696a0',
    fontSize: 13,
  },
  activeChatAvatar: {
    fontSize: 28,
    marginRight: 12,
  },
  headerMeta: {
    flex: 1,
  },
  activeChatName: {
    color: '#e9edef',
    fontWeight: 'bold',
    fontSize: 16,
  },
  activeChatStatus: {
    color: '#8696a0',
    fontSize: 12,
  },
  messageArea: {
    flex: 1,
    paddingHorizontal: 24,
  },
  messageAreaContent: {
    paddingVertical: 16,
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
    maxWidth: '75%',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    position: 'relative',
  },
  bubbleMe: {
    backgroundColor: '#005c4b', // WhatsApp Dark Green Msg Bubble
    borderTopRightRadius: 0,
  },
  bubbleOther: {
    backgroundColor: '#202c33', // WhatsApp Dark Grey Msg Bubble
    borderTopLeftRadius: 0,
  },
  typingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#202c33',
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  typingText: {
    color: '#8696a0',
    fontSize: 14,
    marginLeft: 10,
  },
  bubbleText: {
    color: '#e9edef',
    fontSize: 15,
    lineHeight: 20,
  },
  bubbleFooter: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    marginTop: 4,
  },
  bubbleTime: {
    color: '#8696a0',
    fontSize: 10,
    marginRight: 4,
  },
  checkIcon: {
    marginLeft: 2,
  },
  inputBar: {
    height: 62,
    backgroundColor: '#202c33',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  inputIconButton: {
    padding: 8,
  },
  chatTextInput: {
    flex: 1,
    backgroundColor: '#2a3942',
    color: '#e9edef',
    borderRadius: 8,
    height: 42,
    paddingHorizontal: 16,
    marginHorizontal: 12,
    fontSize: 15,
    outlineStyle: 'none',
  },
  sendButton: {
    padding: 10,
  },
});
