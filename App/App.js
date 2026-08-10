import { StatusBar } from 'expo-status-bar';
import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  Image,
  ActivityIndicator
} from 'react-native';
import {
  Search,
  MoreVertical,
  Paperclip,
  Smile,
  Mic,
  ArrowLeft,
  CheckCheck
} from 'lucide-react-native';
import { initialChats, getSimulatedResponse } from './src/mockData';
import { styles } from './src/styles';
import Profile from './src/Profile';

export default function App() {
  const [activeChat] = useState(initialChats[0]);
  const [messages, setMessages] = useState(initialChats[0].messages);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentScreen, setCurrentScreen] = useState('chat');

  const scrollViewRef = useRef(null);

  useEffect(() => {
    if (scrollViewRef.current) {
      setTimeout(() => {
        scrollViewRef.current.scrollToEnd({ animated: true });
      }, 50);
    }
  }, [messages, isTyping]);

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

    setMessages(prev => [...prev, newMsg]);

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
      setMessages(prev => [...prev, botMsg]);
    }, 1200);
  };

  if (currentScreen === 'profile') {
    return (
      <Profile activeChat={activeChat} goBack={() => setCurrentScreen('chat')} />
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" backgroundColor="#054c44" />
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.headerLeft}
            activeOpacity={0.7}
            onPress={() => setCurrentScreen('profile')}
          >
            <TouchableOpacity style={styles.backButton}>
              <ArrowLeft size={24} color="#fff" />
            </TouchableOpacity>
            <Image source={activeChat.avatar} style={styles.avatarImage} />
            <View style={styles.headerTitleContainer}>
              <Text style={styles.headerName}>{activeChat.name}</Text>
              <Text style={styles.headerStatus}>{activeChat.status}</Text>
            </View>
          </TouchableOpacity>
          <View style={styles.headerRight}>
            <TouchableOpacity style={styles.iconButton}>
              <MoreVertical size={22} color="#fff" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Chat Area */}
        <View style={styles.chatAreaWrapper}>
          {/* Solid fallback color if background pattern is unavailable */}
          <View style={styles.chatBackground} />

          <ScrollView
            ref={scrollViewRef}
            style={styles.messageArea}
            contentContainerStyle={styles.messageAreaContent}
          >
            {messages.map((msg, index) => {
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
                  <ActivityIndicator size="small" color="#075E54" />
                  <Text style={styles.typingText}>typing...</Text>
                </View>
              </View>
            )}
          </ScrollView>
        </View>

        {/* Input Bar */}
        <View style={styles.inputBar}>
          <View style={styles.inputContainer}>
            <TouchableOpacity style={styles.inputIconButton}>
              <Smile size={24} color="#8696a0" />
            </TouchableOpacity>

            <TextInput
              placeholder="Type a message"
              placeholderTextColor="#8696a0"
              style={styles.chatTextInput}
              value={inputText}
              onChangeText={setInputText}
              onSubmitEditing={handleSendMessage}
            />

            <TouchableOpacity style={styles.inputIconButton}>
              <Paperclip size={24} color="#8696a0" />
            </TouchableOpacity>
          </View>

          {/* Voice/Send Button */}
          <TouchableOpacity style={styles.micButton} onPress={inputText.trim() ? handleSendMessage : null}>
            <View style={styles.micCircle}>
              <Mic size={24} color="#fff" />
            </View>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}


