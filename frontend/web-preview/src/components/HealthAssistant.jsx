import { useState } from 'react';
import { FaComments, FaUser, FaBook, FaExclamationTriangle, FaEllipsisH } from 'react-icons/fa';
import { FaMicrophone, FaPaperPlane } from 'react-icons/fa';
import { FaAmbulance, FaHospital, FaUserMd, FaFirstAid } from 'react-icons/fa';


export default function HealthAssistant() {
  const [chatOpen, setChatOpen] = useState(true);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-between font-sans">
      {/* Chat Header */}
      <div className="bg-white shadow-md p-4">
        <h2 className="text-lg font-semibold text-gray-800">RuralHealth.AI</h2>
      </div>

      {/* Chat Window */} 
      <div className="flex justify-start">
        {chatOpen && ( 
          <div className="bg-blue-50 p-4 rounded-lg shadow-sm max-w-md">
            <p className="text-sm text-gray-700">
              Hello! I’m your health assistant. I can help with first-aid, symptom assessment, and health guidance. What would you like to know?
            </p>
            <p className="text-xs text-right text-gray-500 mt-2">11:56 PM</p>
          </div>
        )}
      </div>

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

      {/* Chat Input */}
      <div className="px-4 bg-white border-t">
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
      <nav className="flex justify-around items-center bg-white border-t py-2 text-sm text-gray-600">
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
  );
}