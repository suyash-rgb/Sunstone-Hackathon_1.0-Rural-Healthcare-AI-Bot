export const initialChats = [
  {
    id: 'ai-bot',
    name: 'AarogyaMitra (AI Health Bot)',
    avatar: '/logo-removebg-preview.png',
    status: 'online',
    subtitle: 'AI Health Assistant',
    messages: [
      {
        id: 'm1',
        text: 'Namaste! I am AarogyaMitra, your Rural Healthcare Assistant. How can I help you today?',
        sender: 'other',
        time: '10:00 AM'
      },
      {
        id: 'm2',
        text: 'You can ask me about common symptoms, health hygiene, pregnancy care, vaccination schedules, or telemedicine guidance.',
        sender: 'other',
        time: '10:01 AM'
      }
    ]
  },
  {
    id: 'asha-seema',
    name: 'ASHA Seema Devi',
    avatar: '👩',
    status: 'online',
    subtitle: 'Community Health Worker',
    messages: [
      {
        id: 'm3',
        text: 'Hello, did you take your weekly iron tablet?',
        sender: 'other',
        time: 'Yesterday'
      },
      {
        id: 'm4',
        text: 'Yes, Seema di. I took it after lunch.',
        sender: 'me',
        time: 'Yesterday'
      },
      {
        id: 'm5',
        text: 'Great. The doctor will visit our village sub-centre this Thursday for monthly checkups.',
        sender: 'other',
        time: 'Yesterday'
      }
    ]
  },
  {
    id: 'dr-verma',
    name: 'Dr. Alok Verma (Telehealth)',
    avatar: '👨‍⚕️',
    status: 'offline',
    subtitle: 'Primary Care Physician',
    messages: [
      {
        id: 'm6',
        text: 'Please share your blood pressure readings from this morning.',
        sender: 'other',
        time: '2 days ago'
      },
      {
        id: 'm7',
        text: 'It was 125/80 mmHg, doctor.',
        sender: 'me',
        time: '2 days ago'
      },
      {
        id: 'm8',
        text: 'Perfect. Continue taking the prescribed tablet once daily after breakfast. Do not skip.',
        sender: 'other',
        time: '2 days ago'
      }
    ]
  }
];

export function getSimulatedResponse(userMessage, chatName) {
  const query = userMessage.toLowerCase();
  
  if (chatName.includes('AI Bot') || chatName.includes('AarogyaMitra')) {
    if (query.includes('hello') || query.includes('hi') || query.includes('namaste')) {
      return "Namaste! I hope you are doing well. Please tell me what health issues or symptoms you'd like guidance on today.";
    }
    if (query.includes('fever') || query.includes('temp') || query.includes('bukhar')) {
      return "Fever can be caused by infections. Make sure the patient stays hydrated and rests. If temperature is over 101°F, apply a clean damp cloth to the forehead. You should consult ASHA worker Seema or contact Dr. Verma via telehealth if it persists for more than 24 hours.";
    }
    if (query.includes('cough') || query.includes('cold') || query.includes('khansi')) {
      return "For dry or wet cough, keep hydrated with warm water. Steam inhalation can relieve nasal congestion. If accompanied by breathing difficulties, seek immediate medical attention at the village sub-centre.";
    }
    if (query.includes('pregnant') || query.includes('pregnancy') || query.includes('delivery')) {
      return "During pregnancy, regular antenatal checkups (at least 4) are vital. Take Iron & Folic Acid supplements, eat nutritious food, and ensure tetanus vaccination is complete. Please sync with ASHA Seema Devi for arranging local checkups.";
    }
    if (query.includes('vaccin') || query.includes('teeka') || query.includes('injection')) {
      return "Child immunization protects against 12 vaccine-preventable diseases. Ensure your child gets BCB, OPV, and Hepatitis B at birth, followed by regular pentavalent doses. Check with ASHA Seema for the next immunization camp date.";
    }
    if (query.includes('bp') || query.includes('blood pressure') || query.includes('hypertension')) {
      return "Regular monitoring of blood pressure is important. Limit salt intake, exercise regularly, and take medications exactly as prescribed. Contact Dr. Verma to share your daily readings.";
    }
    return "Thank you for sharing. As an AI Assistant, I can provide general information, but for diagnosis and prescriptions, please contact ASHA Seema or consult Dr. Alok Verma.";
  } 
  
  if (chatName.includes('ASHA')) {
    return "Dhanyawad. I have received your message. I am currently checking up on families in the next street and will visit you shortly or call you back.";
  }
  
  if (chatName.includes('Dr.')) {
    return "Thank you. This is an automated response. Dr. Verma is currently attending to patients. If this is an emergency, please visit the nearest Community Health Centre (CHC).";
  }

  return "Received. We will get back to you soon.";
}
