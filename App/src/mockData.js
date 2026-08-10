export const initialChats = [
  {
    id: 'ai-bot',
    name: 'Aarogya Mitra',
    avatar: require('../assets/logo-removebg-preview.png'),
    status: 'last seen today at 15.24',
    messages: [
      {
        id: 'msg-1',
        text: 'Welcome to Rural HealthBot!\nHow can I assist you Today?',
        sender: 'other',
        time: '14.09'
      },
      {
        id: 'msg-2',
        text: 'hello',
        sender: 'me',
        time: '14.21'
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
