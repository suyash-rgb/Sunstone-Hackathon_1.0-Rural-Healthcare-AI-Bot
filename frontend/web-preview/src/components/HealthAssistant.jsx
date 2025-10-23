import { useState, useEffect } from 'react';
import { FaComments, FaUser, FaBook, FaExclamationTriangle, FaEllipsisH } from 'react-icons/fa';
import { FaMicrophone, FaPaperPlane } from 'react-icons/fa';
import { FaAmbulance, FaHospital, FaUserMd, FaFirstAid } from 'react-icons/fa';


export default function HealthAssistant() {
  const [chatOpen, setChatOpen] = useState(true);
  const [showMessage, setShowMessage] = useState(false);
  const [language, setLanguage] = useState('en');

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowMessage(true);
    }, 300); // delay in ms

    return () => clearTimeout(timer);
  }, []);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी' },
    { code: 'bn', name: 'বাংলা' },
    { code: 'te', name: 'తెలుగు' },
    { code: 'ta', name: 'தமிழ்' },
    { code: 'mr', name: 'मराठी' },
    { code: 'gu', name: 'ગુજરાતી' },
    { code: 'kn', name: 'ಕನ್ನಡ' },
    { code: 'ml', name: 'മലയാളം' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ' }
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-between font-sans">
      {/* Chat Header */}
      <div className="bg-white shadow-md p-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-800">RuralHealth.AI</h2>
          <select 
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-3 py-1 mr-5 rounded-md border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
          >
            {languages.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Chat Window */} 
      <div className="flex justify-start px-4 py-2 mb-36 pb-36 overflow-y-auto">
        {chatOpen && ( 
          <div className="bg-blue-50 p-4 rounded-lg shadow-sm max-w-md ">
            <p className="text-sm text-gray-700">
              Hello! I’m your health assistant. I can help with first-aid, symptom assessment, and health guidance. What would you like to know?
            </p>
            <p className="text-xs text-right text-gray-500 mt-2">11:56 PM</p>
          </div>
        )}
      </div>

      {/*  Action Buttons */}
      <div className="grid grid-cols-4 gap-4 px-8">
       <button className="bg-red-500 text-white py-4 text-lg rounded-lg shadow hover:bg-red-600">
          <FaAmbulance className="inline-block mr-2 text-xl" /> Emergency
       </button>
       <button className="bg-blue-500 text-white py-4 text-lg rounded-lg shadow hover:bg-blue-600">
          <FaHospital className="inline-block mr-2 text-xl" /> Find Hospital
       </button>
       <button className="bg-blue-500 text-white py-4 text-lg rounded-lg shadow hover:bg-blue-600">
          <FaUserMd className="inline-block mr-2 text-xl" /> Book Doctor
       </button>
       <button className="bg-blue-500 text-white py-4 text-lg rounded-lg shadow hover:bg-blue-600">
          <FaFirstAid className="inline-block mr-2 text-xl" /> First Aid
       </button>
      </div>

      {/* Bottom Section: Chat Input + Navigation */}
<div className="bg-white border-t">
  {/* Chat Input */}
  <div className="px-4 py-2">
    <div className="flex items-center gap-2">
      <input
        type="text"
        placeholder="Type your symptoms or question..."
        className="flex-1 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      <button
        title="Voice Input"
        className="p-2 bg-gray-100 rounded-full hover:bg-gray-200 focus:outline-none"
      >
        <FaMicrophone className="text-xl text-gray-600" />
      </button>
      <button
        title="Send"
        className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 focus:outline-none"
      >
        <FaPaperPlane className="text-xl" />
      </button>
    </div>
  </div>

  {/* Bottom Navigation */}
  <nav className="flex justify-around items-center border-t py-2 text-sm text-gray-600">
    <div className="flex flex-col items-center">
      <FaComments className="text-xl" />
      <span>Chats</span>
    </div>
    <div className="flex flex-col items-center">
      <FaUser className="text-xl" />
      <span>Profile</span>
    </div>
    <div className="flex flex-col items-center">
      <FaBook className="text-xl" />
      <span>Resources</span>
    </div>
    <div className="flex flex-col items-center">
      <FaEllipsisH className="text-xl" />
      <span>More</span>
    </div>
  </nav>
</div>
    </div>
  );
}