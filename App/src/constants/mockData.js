export const initialChats = [
  {
    id: 'meta-ai',
    name: 'Meta AI',
    avatar: require('../../assets/meta-ai-logo.png'),
    isMetaAI: true,
    isOfficial: true,
    status: 'AI Assistant',
    messages: [
      {
        id: 'm-msg-1',
        text: 'Hi! I am Meta AI. How can I help you today?',
        sender: 'other',
        time: '10:00'
      }
    ]
  },
  {
    id: 'you',
    name: 'Leo (You)',
    avatar: require('../../assets/leo_profile_pic.jpg'),
    status: 'you',
    messages: [
      {
        id: 'my-msg-1',
        text: 'I am OG now, I do not pay homage!',
        sender: 'me',
        time: '00:00'
      }
    ]
  },
  {
    id: 'ai-bot',
    name: 'Aarogya Mitra',
    avatar: require('../../assets/logo-removebg-preview.png'),
    isOfficial: true,
    status: 'last seen today at 15.24',
    messages: [
      {
        id: 'msg-1',
        text: 'Welcome to Aarogya Mitra! How can I assist you today?',
        sender: 'other',
        time: '14.09',
        buttons: [
          '📍 Locate a Healthcare Facility',
          'Change Language',
          'Book a Consultation',
          'Talk to a Doctor',
          '🚨 EMERGENCY/HELP'
        ]
      },
      {
        id: 'msg-2',
        text: 'Type /info for more information.',
        sender: 'other',
        time: '14.09'
      }
    ]
  },
  {
    id: 'papa',
    name: 'Papa',
    avatar: null,
    status: 'Dad',
    messages: [
      {
        id: 'papa-msg-1',
        text: 'Beta chai bna liyo',
        sender: 'other',
        time: '04:00'
      }
    ]
  },
  {
    id: 'mummy',
    name: 'Mummy',
    avatar: null,
    status: 'Mom',
    messages: [
      {
        id: 'mummy-msg-1',
        text: 'Dhaniya lete aana',
        sender: 'other',
        time: '10:00'
      }
    ]
  },
  {
    id: 'ajay',
    name: 'Ajay Clg',
    avatar: null,
    status: 'Clg Friend',
    messages: [
      {
        id: 'ajay-msg-1',
        text: 'Razorpay Integration success bhai',
        sender: 'other',
        time: '12:00'
      }
    ]
  },
  {
    id: 'john-doe',
    name: 'John Doe',
    avatar: null,
    status: 'last seen recently',
    messages: [
      {
        id: 'j-msg-1',
        text: 'Hey, are we still meeting up later?',
        sender: 'other',
        time: '09:45'
      }
    ]
  },
  {
    id: 'jane-smith',
    name: 'Jane Smith',
    avatar: null,
    status: 'last seen yesterday at 18:00',
    messages: [
      {
        id: 'js-msg-1',
        text: 'Thanks for the document! I will review it.',
        sender: 'other',
        time: 'Yesterday'
      }
    ]
  },
  {
    id: 'ajeet',
    name: 'Ajeet Clg',
    avatar: null,
    status: 'Friend',
    messages: [
      {
        id: 'ajeet-msg-1',
        text: 'Bhai project bn gya?',
        sender: 'other',
        time: '10:00'
      }
    ]
  }
];

export const getSimulatedResponse = (text, botName) => {
  const lowerText = text.toLowerCase();
  if (lowerText.includes('fever') || lowerText.includes('headache')) {
    return "I'm sorry to hear you're not feeling well. For a fever or headache, please ensure you rest and drink plenty of fluids. If symptoms persist for more than 48 hours, please visit your nearest primary healthcare center.";
  }
  if (lowerText.includes('appointment')) {
    return "I can help with that. Which department would you like to visit? (e.g., General Medicine, Pediatrics, Maternity)";
  }
  if (lowerText.includes('thank')) {
    return "You're welcome! Stay healthy. Let me know if you need anything else.";
  }
  return `Thank you for reaching out to ${botName}. A healthcare representative will get back to you shortly. For emergencies, please call the national helpline.`;
};
