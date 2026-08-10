import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Image,
  ActivityIndicator
} from 'react-native';
import {
  MoreVertical,
  Paperclip,
  Smile,
  Mic,
  ArrowLeft,
  CheckCheck,
  Camera,
  FileText,
  BadgeCheck
} from 'lucide-react-native';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import * as Location from 'expo-location';
import { getSimulatedResponse } from '../constants/mockData';
import { styles } from '../constants/styles';
import RecordingBar from '../components/RecordingBar';
import AudioMessage from '../components/AudioMessage';

export default function ChatScreen({ chat, goBack, openProfile }) {
  const [messages, setMessages] = useState(chat.messages || []);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const scrollViewRef = useRef(null);

  const handleSendMessage = () => {
    if (inputText.trim() === '') return;

    const newMsg = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'me',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, newMsg]);
    setInputText('');

    if (chat.isOfficial) {
      simulateBotResponse(inputText);
    }
  };

  const handleAttachment = async () => {
    try {
      const file = await DocumentPicker.getDocumentAsync({
        type: ['image/*', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'],
        copyToCacheDirectory: true
      });

      if (file.type === 'success' || !file.canceled) {
        const isImage = file.mimeType?.startsWith('image/') || file.name?.match(/\.(jpeg|jpg|gif|png)$/i);
        if (isImage) {
          sendMediaMessage({ type: 'image', uri: file.uri });
        } else {
          sendMediaMessage({ type: 'document', name: file.name, uri: file.uri });
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCamera = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (!permissionResult.granted) {
      alert("Camera permission is required!");
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      quality: 0.5,
    });
    if (!result.canceled && result.assets && result.assets.length > 0) {
      sendMediaMessage({ type: 'image', uri: result.assets[0].uri });
    }
  };

  const sendMediaMessage = (mediaData) => {
    const newMsg = {
      id: Date.now().toString(),
      sender: 'me',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      ...mediaData
    };
    setMessages(prev => [...prev, newMsg]);
  };

  const simulateBotResponse = (userText) => {
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      let botReply = '';
      if (chat.isMetaAI) {
        botReply = "That's interesting! I'm an AI, so I don't have personal experiences, but I can help you find more information about that.";
      } else {
        botReply = getSimulatedResponse(userText, chat.name);
      }

      const botMsg = {
        id: (Date.now() + 1).toString(),
        text: botReply,
        sender: 'other',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMsg]);
    }, 1200);
  };

  return (
    <KeyboardAvoidingView
      style={styles.keyboardView}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.headerLeft}
          activeOpacity={0.7}
          onPress={openProfile}
        >
          <TouchableOpacity style={styles.backButton} onPress={goBack}>
            <ArrowLeft size={24} color="#fff" />
          </TouchableOpacity>
          {chat.avatar ? (
            <Image source={chat.avatar} style={styles.avatarImage} />
          ) : (
            <View style={[styles.avatarImage, { backgroundColor: '#ccc', justifyContent: 'center', alignItems: 'center' }]}>
              <Text style={{ fontSize: 18, color: '#fff' }}>{chat.name.charAt(0)}</Text>
            </View>
          )}
          <View style={styles.headerTitleContainer}>
            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
              <Text style={styles.headerName}>{chat.name}</Text>
              {chat.isOfficial && <BadgeCheck size={16} color="#53BDEB" style={{ marginLeft: 4 }} fill="#fff" />}
            </View>
            <Text style={styles.headerStatus}>{chat.status}</Text>
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
        <View style={styles.chatBackground} />

        <ScrollView
          ref={scrollViewRef}
          style={styles.messageArea}
          contentContainerStyle={styles.messageAreaContent}
          onContentSizeChange={() => scrollViewRef.current?.scrollToEnd({ animated: true })}
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
                  {msg.buttons && (
                    <View style={styles.actionButtonsContainer}>
                      {msg.buttons.map((btn, i) => (
                        <TouchableOpacity
                          key={i}
                          style={styles.actionButton}
                          onPress={() => {
                            if (btn.includes('Locate a Healthcare Facility')) {
                              (async () => {
                                try {
                                  // Immediate feedback so user knows it's working
                                  const tempMsg = {
                                    id: Date.now().toString(),
                                    text: btn,
                                    sender: 'me',
                                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                  };
                                  setMessages(prev => [...prev, tempMsg]);
                                  setIsTyping(true);

                                  let { status } = await Location.requestForegroundPermissionsAsync();
                                  if (status !== 'granted') {
                                    setTimeout(() => {
                                      setIsTyping(false);
                                      const botReply = "I need location access to find nearby healthcare facilities.\n\nTo enable it:\n• Android: Settings > Apps > Aarogya Mitra > Permissions > Location\n• iOS: Settings > Privacy > Location Services > Aarogya Mitra\n\nPlease enable it and try again.";
                                      const botMsg = {
                                        id: Date.now().toString(),
                                        text: botReply,
                                        sender: 'other',
                                        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                      };
                                      setMessages(prev => [...prev, botMsg]);
                                    }, 1000);
                                    return;
                                  }

                                  // Use getCurrentPositionAsync with low accuracy and timeout to prevent hanging on emulators
                                  let location = await Location.getCurrentPositionAsync({
                                    accuracy: Location.Accuracy.Balanced,
                                    timeout: 10000
                                  });

                                  // If timeout occurs or fails, fallback to last known
                                  if (!location) {
                                    location = await Location.getLastKnownPositionAsync();
                                  }

                                  if (!location) {
                                    throw new Error("Could not get location");
                                  }

                                  const locMsg = {
                                    id: (Date.now() + 1).toString(),
                                    text: `📍 GPS Acquired: Lat ${location.coords.latitude.toFixed(4)}, Lon ${location.coords.longitude.toFixed(4)}`,
                                    sender: 'other',
                                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                  };
                                  setMessages(prev => [...prev, locMsg]);

                                  if (chat.isOfficial) {
                                    setTimeout(() => {
                                      setIsTyping(false);
                                      const botReply = "I have received your location. Finding nearest government hospitals and clinics...\n\n1. District Hospital (2.3 km)\n2. Primary Health Center (4.1 km)\n\nWould you like directions or to book a consultation?";
                                      const botMsg = {
                                        id: (Date.now() + 2).toString(),
                                        text: botReply,
                                        sender: 'other',
                                        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                      };
                                      setMessages(prev => [...prev, botMsg]);
                                    }, 1500);
                                  } else {
                                    setIsTyping(false);
                                  }
                                } catch (error) {
                                  console.error(error);
                                  setTimeout(() => {
                                    setIsTyping(false);
                                    const botReply = "There was an error fetching your location. Please make sure your device's GPS is turned on and try again.";
                                    const botMsg = {
                                      id: Date.now().toString(),
                                      text: botReply,
                                      sender: 'other',
                                      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                    };
                                    setMessages(prev => [...prev, botMsg]);
                                  }, 1000);
                                }
                              })();
                              return;
                            }

                            // Automatically send this button text as a message
                            const newMsg = {
                              id: Date.now().toString(),
                              text: btn,
                              sender: 'me',
                              time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                            };
                            setMessages(prev => [...prev, newMsg]);
                            if (chat.isOfficial) {
                              simulateBotResponse(btn);
                            }
                          }}
                        >
                          <Text style={styles.actionButtonText}>{btn}</Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  )}
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
  );
}
