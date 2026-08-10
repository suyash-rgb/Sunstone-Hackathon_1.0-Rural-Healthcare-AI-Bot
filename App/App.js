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
  CheckCheck,
  Camera,
  FileText,
  Play,
  Pause,
  Trash2
} from 'lucide-react-native';
import { useAudioPlayer, useAudioPlayerStatus } from 'expo-audio';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import { initialChats, getSimulatedResponse } from './src/mockData';
import { styles } from './src/styles';
import Profile from './src/Profile';
import RecordingBar from './src/RecordingBar';

const AudioMessage = ({ uri }) => {
  const player = useAudioPlayer(uri);
  const status = useAudioPlayerStatus(player);

  const togglePlayback = () => {
    if (status.playing) {
      player.pause();
    } else {
      if (status.currentTime >= status.duration && status.duration > 0) {
        player.seekTo(0);
      }
      player.play();
    }
  };


  const formatTime = (seconds) => {
    if (!seconds) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  };

  const progressPercent = status.duration && status.currentTime
    ? (status.currentTime / status.duration) * 100
    : 0;

  return (
    <View style={styles.audioContainer}>
      <TouchableOpacity onPress={togglePlayback} style={styles.audioPlayButton}>
        {status.playing ? <Pause size={24} color="#00a884" /> : <Play size={24} color="#00a884" />}
      </TouchableOpacity>
      
      <View style={styles.audioProgressTrack}>
        <View style={[styles.audioProgressBar, { width: `${progressPercent}%` }]} />
        <View style={[styles.audioProgressDot, { left: `${progressPercent}%` }]} />
      </View>
      
      <Text style={styles.audioDuration}>
        {formatTime(status.currentTime || status.duration)}
      </Text>
      
      <Mic size={16} color="#00A884" style={{ marginLeft: 6 }} />
    </View>
  );
};

export default function App() {
  const [activeChat] = useState(initialChats[0]);
  const [messages, setMessages] = useState(initialChats[0].messages);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentScreen, setCurrentScreen] = useState('chat');
  const [isRecording, setIsRecording] = useState(false);

  const scrollViewRef = useRef(null);

  useEffect(() => {
    if (scrollViewRef.current) {
      setTimeout(() => {
        scrollViewRef.current.scrollToEnd({ animated: true });
      }, 50);
    }
  }, [messages, isTyping]);

  const handleCamera = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (permissionResult.granted === false) {
      alert("You've refused to allow this app to access your camera!");
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 1,
    });
    if (!result.canceled) {
      sendMediaMessage({ type: 'image', uri: result.assets[0].uri });
    }
  };

  const handleAttachment = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['image/*', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'],
        copyToCacheDirectory: true,
      });
      if (!result.canceled) {
        const file = result.assets[0];
        const isImage = file.mimeType?.startsWith('image/') || file.name.match(/\.(jpeg|jpg|gif|png)$/i);
        if (isImage) {
          sendMediaMessage({ type: 'image', uri: file.uri });
        } else {
          sendMediaMessage({ type: 'document', uri: file.uri, name: file.name });
        }
      }
    } catch (err) {
      console.log('Error picking document', err);
    }
  };

  const sendMediaMessage = (mediaPayload) => {
    const newMsg = {
      id: `msg-${Date.now()}`,
      sender: 'me',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      ...mediaPayload
    };

    setMessages(prev => [...prev, newMsg]);

    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      const botReply = getSimulatedResponse("I uploaded a file", activeChat.name);
      const botMsg = {
        id: `msg-bot-${Date.now()}`,
        text: botReply,
        sender: 'other',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMsg]);
    }, 1200);
  };

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
                    {msg.type === 'image' && (
                      <Image source={{ uri: msg.uri }} style={styles.bubbleImage} />
                    )}
                    {msg.type === 'document' && (
                      <View style={styles.documentContainer}>
                        <View style={styles.documentIconBox}>
                          <FileText size={20} color="#fff" />
                        </View>
                        <Text style={styles.documentName} numberOfLines={1}>{msg.name}</Text>
                      </View>
                    )}
                    {msg.type === 'audio' && <AudioMessage uri={msg.uri} />}
                    {msg.text ? <Text style={styles.bubbleText}>{msg.text}</Text> : null}
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
          {isRecording ? (
            <RecordingBar 
              onSend={(uri) => {
                sendMediaMessage({ type: 'audio', uri });
                setIsRecording(false);
              }}
              onCancel={() => setIsRecording(false)}
            />
          ) : (
            <>
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

                <TouchableOpacity style={styles.inputIconButton} onPress={handleAttachment}>
                  <Paperclip size={24} color="#8696a0" />
                </TouchableOpacity>
                <TouchableOpacity style={styles.inputIconButton} onPress={handleCamera}>
                  <Camera size={24} color="#8696a0" />
                </TouchableOpacity>
              </View>

              <TouchableOpacity style={styles.micButton} onPress={inputText.trim() ? handleSendMessage : () => setIsRecording(true)}>
                <View style={styles.micCircle}>
                  <Mic size={24} color="#fff" />
                </View>
              </TouchableOpacity>
            </>
          )}
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}


