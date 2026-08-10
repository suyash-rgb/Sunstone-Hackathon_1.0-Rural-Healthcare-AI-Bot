import React from 'react';
import { View, Text, TouchableOpacity, FlatList, Image } from 'react-native';
import { Search, MoreVertical, Camera, BadgeCheck } from 'lucide-react-native';
import { styles } from '../constants/styles';

export default function ChatListScreen({ chats, onSelectChat }) {
  const renderItem = ({ item }) => {
    const lastMessage = item.messages.length > 0 ? item.messages[item.messages.length - 1] : null;

    return (
      <TouchableOpacity style={styles.chatListItem} onPress={() => onSelectChat(item)}>
        {item.avatar ? (
          <Image source={item.avatar} style={styles.chatListAvatar} />
        ) : (
          <View style={[styles.chatListAvatar, { backgroundColor: item.isMetaAI ? '#25D366' : '#ccc', justifyContent: 'center', alignItems: 'center' }]}>
            {item.isMetaAI ? (
               <Text style={{ fontSize: 24 }}>🤖</Text>
            ) : (
               <Text style={{ fontSize: 20, color: '#fff' }}>{item.name.charAt(0)}</Text>
            )}
          </View>
        )}
        
        <View style={styles.chatListDetails}>
          <View style={styles.chatListHeader}>
            <View style={{ flexDirection: 'row', alignItems: 'center' }}>
              <Text style={styles.chatListName} numberOfLines={1}>{item.name}</Text>
              {item.isOfficial && <BadgeCheck size={14} color="#53BDEB" style={{ marginLeft: 4 }} fill="#fff" />}
            </View>
            {lastMessage && (
              <Text style={styles.chatListTime}>{lastMessage.time}</Text>
            )}
          </View>
          {lastMessage && (
            <Text style={styles.chatListLastMessage} numberOfLines={1}>
              {lastMessage.type === 'audio' ? '🎵 Audio message' : 
               lastMessage.type === 'image' ? '📷 Photo' : 
               lastMessage.type === 'document' ? '📄 Document' : 
               lastMessage.text}
            </Text>
          )}
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {/* WhatsApp Home Header */}
      <View style={styles.homeHeader}>
        <Text style={styles.homeTitle}>WhatsApp</Text>
        <View style={styles.homeIcons}>
          <TouchableOpacity style={styles.iconButton}>
            <Camera size={24} color="#fff" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.iconButton}>
            <Search size={24} color="#fff" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.iconButton}>
            <MoreVertical size={24} color="#fff" />
          </TouchableOpacity>
        </View>
      </View>
      
      {/* Tabs */}
      <View style={styles.homeTabs}>
        <View style={[styles.tabItem, styles.activeTab]}>
          <Text style={styles.activeTabText}>Chats</Text>
        </View>
        <View style={styles.tabItem}>
          <Text style={styles.tabText}>Updates</Text>
        </View>
        <View style={styles.tabItem}>
          <Text style={styles.tabText}>Calls</Text>
        </View>
      </View>

      <FlatList
        data={chats}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.chatListContainer}
      />
    </View>
  );
}
