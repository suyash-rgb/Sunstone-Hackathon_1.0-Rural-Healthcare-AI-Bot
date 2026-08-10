import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Switch,
  Platform,
  StatusBar
} from 'react-native';
import {
  ArrowLeft,
  MoreVertical,
  Forward,
  Building2,
  Globe,
  UserPlus,
  Info,
  Bell,
  Image as ImageIcon,
  Lock,
  Shield,
  Languages,
  Users,
  UserRoundPlus,
  Ban,
  BadgeCheck,
  ThumbsDown
} from 'lucide-react-native';

export default function Profile({ activeChat, goBack }) {
  const [chatLock, setChatLock] = React.useState(false);
  const [translate, setTranslate] = React.useState(false);

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.headerButton} onPress={goBack}>
          <ArrowLeft size={24} color="#111B21" />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Image source={activeChat.avatar} style={styles.smallAvatar} />
          <Text style={styles.headerTitle} numberOfLines={1}>{activeChat.name}</Text>
          <BadgeCheck size={16} color="#53BDEB" style={{ marginLeft: 4, marginTop: 2 }} fill="#fff" />
        </View>
        <TouchableOpacity style={styles.headerButton}>
          <MoreVertical size={24} color="#111B21" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Hero Section */}
        <View style={styles.sectionCard}>
          <View style={styles.heroContainer}>
            <Image source={activeChat.avatar} style={styles.heroAvatar} />
            <View style={styles.heroNameContainer}>
              <Text style={styles.heroName}>{activeChat.name}</Text>
              <BadgeCheck size={22} color="#53BDEB" fill="#fff" style={{ marginLeft: 6, marginTop: 4 }} />
            </View>
            <Text style={styles.heroPhone}>+91 22 2275 0353</Text>

            <TouchableOpacity style={styles.shareButton}>
              <Forward size={24} color="#00A884" />
            </TouchableOpacity>
            <Text style={styles.shareText}>Share</Text>
          </View>
        </View>

        {/* Business Details List */}
        <View style={styles.sectionCard}>
          <View style={styles.listItem}>
            <Building2 size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Public and government service</Text>
            </View>
          </View>

          <View style={styles.listItem}>
            <Building2 size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>This is official business account of {activeChat.name}.</Text>
            </View>
          </View>

          <TouchableOpacity style={styles.listItem}>
            <Globe size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextLink} numberOfLines={1}>https://www.ruralhealth.gov.in</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={styles.listItem}>
            <UserPlus size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Add to contacts</Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Business Account Info */}
        <View style={styles.sectionCard}>
          <View style={styles.listItem}>
            <Info size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Business Account</Text>
              <Text style={styles.listTextSecondary}>This account uses WhatsApp Business</Text>
            </View>
          </View>
        </View>

        {/* Settings List */}
        <View style={styles.sectionCard}>
          <TouchableOpacity style={styles.listItem}>
            <Bell size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Notifications</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={styles.listItem}>
            <ImageIcon size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Media visibility</Text>
            </View>
          </TouchableOpacity>

          <View style={styles.listItem}>
            <Lock size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Chat lock</Text>
              <Text style={styles.listTextSecondary}>Lock and hide this chat on this device.</Text>
            </View>
            <Switch
              value={chatLock}
              onValueChange={setChatLock}
              trackColor={{ false: '#E9EDEF', true: '#00A884' }}
              thumbColor={'#fff'}
            />
          </View>

          <View style={styles.listItem}>
            <Shield size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Security</Text>
              <Text style={styles.listTextSecondary}>
                This business uses a secure service from Meta to manage this chat. <Text style={styles.listTextLink}>Learn more</Text>
              </Text>
            </View>
          </View>

          <View style={styles.listItem}>
            <Languages size={24} color="#8696A0" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Translate messages</Text>
            </View>
            <Switch
              value={translate}
              onValueChange={setTranslate}
              trackColor={{ false: '#E9EDEF', true: '#00A884' }}
              thumbColor={'#fff'}
            />
          </View>
        </View>

        {/* Groups & Actions */}
        <Text style={styles.sectionHeader}>No groups in common</Text>
        <View style={styles.sectionCard}>
          <TouchableOpacity style={styles.listItem}>
            <View style={styles.greenCircleIcon}>
              <Users size={20} color="#fff" />
            </View>
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Create group with {activeChat.name}</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={styles.listItem}>
            <View style={styles.greenCircleIcon}>
              <UserRoundPlus size={20} color="#fff" />
            </View>
            <View style={styles.listContent}>
              <Text style={styles.listTextPrimary}>Add to groups</Text>
              <Text style={styles.listTextSecondary}>Add this contact to groups you're in.</Text>
            </View>
          </TouchableOpacity>
        </View>

        <View style={[styles.sectionCard, { marginBottom: 40 }]}>
          <TouchableOpacity style={styles.listItem}>
            <Ban size={24} color="#EA0038" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={[styles.listTextPrimary, { color: '#EA0038' }]}>Block business</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={styles.listItem}>
            <ThumbsDown size={24} color="#EA0038" style={styles.listIcon} />
            <View style={styles.listContent}>
              <Text style={[styles.listTextPrimary, { color: '#EA0038' }]}>Report business</Text>
            </View>
          </TouchableOpacity>
        </View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
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
