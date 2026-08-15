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
  ActivityIndicator,
  Modal
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
  BadgeCheck,
  User,
  X
} from 'lucide-react-native';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import * as Location from 'expo-location';
import { getSimulatedResponse, mockDoctors } from '../constants/mockData';
import { translations } from '../constants/translations';

const languages = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'hi', name: 'Hindi', native: 'हिंदी' },
  { code: 'mr', name: 'Marathi', native: 'मराठी' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'as', name: 'Assamese', native: 'অসমীয়া' },
  { code: 'brx', name: 'Bodo', native: 'बड़ो' },
  { code: 'doi', name: 'Dogri', native: 'डोगरी' },
  { code: 'ks', name: 'Kashmiri', native: 'कॉशुर' },
  { code: 'gom', name: 'Konkani', native: 'कोंकणी' },
  { code: 'mai', name: 'Maithili', native: 'मैथिली' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം' },
  { code: 'mni', name: 'Manipuri', native: 'মৈতৈলোন্' },
  { code: 'ne', name: 'Nepali', native: 'नेपाली' },
  { code: 'or', name: 'Odia', native: 'ଓଡ଼ିଆ' },
  { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
  { code: 'sa', name: 'Sanskrit', native: 'संस्कृतम्' },
  { code: 'sat', name: 'Santali', native: 'ᱥᱟᱱᱛᱟᱲᱤ' },
  { code: 'sd', name: 'Sindhi', native: 'سنڌي' },
  { code: 'ur', name: 'Urdu', native: 'اردو' }
];
import { styles } from '../constants/styles';
import RecordingBar from '../components/RecordingBar';
import AudioMessage from '../components/AudioMessage';

export default function ChatScreen({ chat, goBack, openProfile }) {
  const [messages, setMessages] = useState(chat.messages || []);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [langModalVisible, setLangModalVisible] = useState(false);
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
      let carouselItems = null;

      const isBook = Object.keys(translations).some(l => userText.toLowerCase().includes(translations[l].book.toLowerCase()) || userText.toLowerCase().includes('book a consultation'));

      if (chat.isMetaAI) {
        botReply = "That's interesting! I'm an AI, so I don't have personal experiences, but I can help you find more information about that.";
      } else if (isBook) {
        botReply = translations[currentLanguage].selectDoc;
        carouselItems = mockDoctors;
      } else {
        botReply = getSimulatedResponse(userText, chat.name);
      }

      const botMsg = {
        id: (Date.now() + 1).toString(),
        text: botReply,
        sender: 'other',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        carouselItems: carouselItems
      };
      setMessages(prev => [...prev, botMsg]);
    }, 1200);
  };

  const handleBookDoctor = (doc) => {
    const userMsg = {
      id: Date.now().toString(),
      text: `I want to book an appointment with ${doc.name}`,
      sender: 'me',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMsg]);

    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      const ticketMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'other',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        type: 'ticket',
        ticketData: {
          doctorName: doc.name,
          specialty: doc.specialty,
          date: new Date(Date.now() + 86400000).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' }),
          time: '11:00 AM (Tele-consult)'
        }
      };
      setMessages(prev => [...prev, ticketMsg]);
    }, 1500);
  };

  const handleSelectLanguage = (langCode) => {
    setLangModalVisible(false);
    setCurrentLanguage(langCode);
    
    // 1. Post user confirmation message
    const confirmText = translations[langCode].confirmLang;
    const userMsg = {
      id: Date.now().toString(),
      text: confirmText,
      sender: 'me',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMsg]);
    
    // 2. Bot welcomes in new language + provides updated buttons
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      const welcomeText = translations[langCode].welcome;
      const botMsg = {
        id: (Date.now() + 1).toString(),
        text: welcomeText,
        sender: 'other',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        buttons: [
          translations[langCode].locate,
          translations[langCode].lang,
          translations[langCode].book,
          translations[langCode].doctor,
          translations[langCode].help
        ]
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
                style={[
                  styles.msgRow,
                  isMe ? styles.msgRowRight : styles.msgRowLeft,
                  msg.carouselItems ? { flexDirection: 'column', alignItems: 'flex-start' } : null
                ]}
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
                  
                  {msg.type === 'ticket' && msg.ticketData && (
                    <View style={styles.ticketContainer}>
                      <View style={styles.ticketHeader}>
                        <Text style={styles.ticketTitle}>Appointment Confirmed</Text>
                        <View style={styles.ticketBadge}>
                          <Text style={styles.ticketBadgeText}>FREE</Text>
                        </View>
                      </View>
                      <View style={styles.ticketRow}>
                        <Text style={styles.ticketLabel}>Doctor:</Text>
                        <Text style={styles.ticketValue}>{msg.ticketData.doctorName}</Text>
                      </View>
                      <View style={styles.ticketRow}>
                        <Text style={styles.ticketLabel}>Specialty:</Text>
                        <Text style={styles.ticketValue}>{msg.ticketData.specialty}</Text>
                      </View>
                      <View style={styles.ticketRow}>
                        <Text style={styles.ticketLabel}>Date:</Text>
                        <Text style={styles.ticketValue}>{msg.ticketData.date}</Text>
                      </View>
                      <View style={styles.ticketRow}>
                        <Text style={styles.ticketLabel}>Time:</Text>
                        <Text style={styles.ticketValue}>{msg.ticketData.time}</Text>
                      </View>
                      <View style={styles.ticketRow}>
                        <Text style={styles.ticketLabel}>Status:</Text>
                        <Text style={[styles.ticketValue, { color: '#00A884' }]}>Confirmed</Text>
                      </View>
                    </View>
                  )}

                  {msg.text ? <Text style={styles.bubbleText}>{msg.text}</Text> : null}
                  {msg.buttons && (
                    <View style={styles.actionButtonsContainer}>
                      {msg.buttons.map((btn, i) => (
                        <TouchableOpacity
                          key={i}
                          style={styles.actionButton}
                          onPress={() => {
                            const isLocate = Object.keys(translations).some(l => btn.includes(translations[l].locate) || btn.includes('Locate a Healthcare Facility'));
                            if (isLocate) {
                              (async () => {
                                try {
                                  // Immediate feedback
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
                                      const botReply = translations[currentLanguage].gps_denied || "I need location access to find nearby healthcare facilities...";
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
                                  
                                  let location = await Location.getCurrentPositionAsync({
                                    accuracy: Location.Accuracy.Balanced,
                                    timeout: 10000
                                  });

                                  if (!location) {
                                      location = await Location.getLastKnownPositionAsync();
                                  }
                                  
                                  if (!location) {
                                      throw new Error("Could not get location");
                                  }
                                  
                                  const locMsg = {
                                    id: (Date.now() + 1).toString(),
                                    text: `${translations[currentLanguage].locAcquired.replace('{lat}', location.coords.latitude.toFixed(4)).replace('{lon}', location.coords.longitude.toFixed(4))}`,
                                    sender: 'me',
                                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                  };
                                  setMessages(prev => [...prev, locMsg]);
                                  
                                  if (chat.isOfficial) {
                                    setTimeout(() => {
                                      setIsTyping(false);
                                      const botReply = translations[currentLanguage].locReply;
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

                            const isLang = Object.keys(translations).some(l => btn.includes(translations[l].lang) || btn.includes('Change Language'));
                            if (isLang) {
                              setLangModalVisible(true);
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

                {msg.carouselItems && (
                  <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    style={styles.carouselContainer}
                  >
                    {msg.carouselItems.map((doc) => (
                      <View key={doc.id} style={styles.doctorCard}>
                        <View style={[styles.doctorImage, { justifyContent: 'center', alignItems: 'center' }]}>
                          <User size={30} color="#8696a0" />
                        </View>
                        <Text style={styles.doctorName}>{doc.name}</Text>
                        <Text style={styles.doctorSpecialty}>{doc.specialty}</Text>
                        <Text style={styles.doctorSub}>{doc.experience}</Text>
                        <Text style={styles.doctorRating}>{doc.rating}</Text>
                        <Text style={styles.doctorSub}>{doc.fees}</Text>
                        <TouchableOpacity
                          style={styles.bookDocButton}
                          onPress={() => handleBookDoctor(doc)}
                        >
                          <Text style={styles.bookDocButtonText}>Book Free Call</Text>
                        </TouchableOpacity>
                      </View>
                    ))}
                  </ScrollView>
                )}
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

      <Modal
        visible={langModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setLangModalVisible(false)}
      >
        <TouchableOpacity 
          style={styles.modalOverlay} 
          activeOpacity={1} 
          onPress={() => setLangModalVisible(false)}
        >
          <View style={styles.modalContentContainer}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Select Language / भाषा चुनें</Text>
              <TouchableOpacity onPress={() => setLangModalVisible(false)}>
                <X size={24} color="#111B21" />
              </TouchableOpacity>
            </View>
            <ScrollView style={styles.langList}>
              {languages.map((lang) => (
                <TouchableOpacity
                  key={lang.code}
                  style={[
                    styles.langOption,
                    currentLanguage === lang.code ? styles.langOptionActive : null
                  ]}
                  onPress={() => handleSelectLanguage(lang.code)}
                >
                  <Text style={styles.langOptionText}>{lang.name}</Text>
                  <Text style={styles.langOptionNative}>{lang.native}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </TouchableOpacity>
      </Modal>
    </KeyboardAvoidingView>
  );
}
