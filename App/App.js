import { StatusBar } from 'expo-status-bar';
import React, { useState } from 'react';
import { View } from 'react-native';
import { SafeAreaView, SafeAreaProvider } from 'react-native-safe-area-context';
import { initialChats } from './src/constants/mockData';
import { styles } from './src/constants/styles';
import ProfileScreen from './src/screens/ProfileScreen';
import ChatScreen from './src/screens/ChatScreen';
import ChatListScreen from './src/screens/ChatListScreen';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('chatList');
  const [activeChat, setActiveChat] = useState(null);

  const handleSelectChat = (chat) => {
    setActiveChat(chat);
    setCurrentScreen('chat');
  };

  const renderScreen = () => {
    if (currentScreen === 'chatList') {
      return (
        <ChatListScreen 
          chats={initialChats} 
          onSelectChat={handleSelectChat} 
        />
      );
    }
    
    if (currentScreen === 'chat') {
      return (
        <ChatScreen 
          key={activeChat.id} // forces remount for fresh chat state
          chat={activeChat} 
          goBack={() => setCurrentScreen('chatList')}
          openProfile={() => setCurrentScreen('profile')}
        />
      );
    }

    if (currentScreen === 'profile') {
      return (
        <ProfileScreen
          activeChat={activeChat}
          goBack={() => setCurrentScreen('chat')}
        />
      );
    }
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" backgroundColor="#054c44" />
        {renderScreen()}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}
