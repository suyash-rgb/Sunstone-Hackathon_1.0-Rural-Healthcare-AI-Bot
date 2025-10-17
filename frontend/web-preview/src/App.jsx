import './App.css'


function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center text-center px-4">
      <h1 className="text-4xl font-bold text-blue-600 mb-4">
        Welcome to Rural HealthBot
      </h1>
      <p className="text-lg text-gray-700 mb-6 max-w-xl">
        Bridging the healthcare gap in Tier 2/3 towns with AI-powered guidance and WhatsApp support.
      </p>
      <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition duration-300">
        Try the Demo
      </button>
    </div>
  );
}

export default App;
