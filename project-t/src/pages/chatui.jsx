import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

const API_URL = "http://127.0.0.1:8000"; 

function ChatUI() {
  const [input, setInput] = useState("");
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hello! How can I help you plan your trip today?" },
  ]);
  const [showItineraryOptions, setShowItineraryOptions] = useState(false);
  const [showVendorCards, setShowVendorCards] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, vendors]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input.trim() };
    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setInput("");
    setShowItineraryOptions(false);
    setShowVendorCards(false);

    try {
      const backendMessages = updatedMessages.map((msg) => ({
        role: msg.role === "bot" ? "ai" : msg.role,
        content: msg.text,
      }));

      const res = await axios.post(`${API_URL}/chat`, {
        chat_history: backendMessages,
      });

      const aiReply = res.data.ai_message;
      const newBotMessage = { role: "bot", text: aiReply };
      setMessages((prev) => [...prev, newBotMessage]);

      if (res.data.next_action === "itinerary_generated") {
        setShowItineraryOptions(true);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = { role: "bot", text: "Something went wrong!" };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleYes = async () => {
    try {
      const response = await axios.get(`${API_URL}/vendors?vendor_type=Driver`);
      const vendorList = response?.data || [];
      setVendors(vendorList);
      setShowVendorCards(true);
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Here are some vendors you might find useful. Tap to select one.",
        },
      ]);
    } catch (error) {
      console.error("Vendor fetch error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Couldn't fetch vendors right now." },
      ]);
    } finally {
      setShowItineraryOptions(false);
    }
  };

  const handleNo = () => {
    setShowItineraryOptions(false);
    setShowVendorCards(false);
    setMessages((prev) => [
      ...prev,
      { role: "bot", text: "Alright! Let me know how else I can help." },
    ]);
  };

  const handleVendorSelect = (vendor) => {
    setSelectedVendor(vendor);
    setMessages((prev) => [
      ...prev,
      {
        role: "bot",
        text: `You selected: ${vendor.business_name} from ${vendor.city}`,
      },
    ]);
    setShowVendorCards(false); // Optionally hide cards after selection
  };

  return (
    <div className="flex flex-col min-h-svh w-full bg-transparent">
<div
  className="fixed top-0 left-0 w-full -z-10 "
  style={{
    minHeight: "100%",
    height: "100%",
    backgroundColor: "#e4c59e",
    backgroundImage: `
      radial-gradient(at 42% 42%, #e4c59e 0%, transparent 60%),
      radial-gradient(at 97% 51%, #af8260 0%, transparent 50%),
      radial-gradient(at 90% 76%, #803d3b 0%, transparent 40%),
      radial-gradient(at 38% 26%, #322c2b 0%, transparent 30%)
    `,
    backgroundSize: "cover",


    
  }}
/>

      <div className="flex-1 overflow-y-auto px-4 md:px-20 lg:px-40 xl:px-96 pt-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`w-full flex my-2 ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`px-4 py-2 rounded-2xl break-words max-w-[90%] ${
                msg.role === "user"
                  ? "bg-[#ab895d]/90 backdrop-blur-sm text-white text-right"
                  : "bg-white/50 backdrop-blur-sm text-gray-800 md:ml-4 text-left prose prose-sm prose-invert"
              }`}
            >
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            </div>
          </div>
        ))}

        {/* Itinerary options */}
        {showItineraryOptions && (
          <div className="flex justify-center gap-4 my-4">
            <button
              onClick={handleYes}
              className="px-4 py-2 bg-[#7ba164] text-white rounded-full"
            >
              Yes
            </button>
            <button
              onClick={handleNo}
              className="px-4 py-2 bg-[#a13e3e] text-white rounded-full"
            >
              No
            </button>
          </div>
        )}

        {showVendorCards && vendors.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 my-6 px-4">
            {vendors.map((vendor) => (
              <div
                key={vendor.id || vendor._id}
                onClick={() => handleVendorSelect(vendor)}
                className="cursor-pointer p-4 rounded-xl shadow-md bg-white hover:bg-gray-200 border border-gray-200 transition"
              >
                <h2 className="text-lg font-semibold">
                  {vendor.business_name}
                </h2>
                <p className="text-sm text-gray-500">{vendor.vendor_type}</p>
                <p className="text-sm text-gray-600">{vendor.city}</p>
                <p className="text-sm mt-1 text-gray-700 italic">
                  {vendor.summary}
                </p>
              </div>
            ))}
          </div>
        )}

        {selectedVendor && (
          <div className="my-4 p-4 rounded-xl bg-blue-50 text-blue-900 border border-blue-300">
            <h3 className="font-bold">Selected Vendor:</h3>
            <p>
              {selectedVendor.business_name} ({selectedVendor.vendor_type}) -{" "}
              {selectedVendor.city}
            </p>
          </div>
        )}

        <div ref={bottomRef}></div>
      </div>

      <div className="sticky bottom-0 z-50 w-full px-4 md:px-20 lg:px-40 xl:px-96 mx-auto pb-3 bg-transparent">
        <div className="flex justify-between rounded-full border border-[#ffffff] p-2 gap-2 backdrop-blur-3xl">
          <input
            type="text"
            placeholder="Ask Anything"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleSend();
              }
            }}
            className="px-3 py-2 border-none bg-transparent text-white placeholder:text-[#fff] focus:outline-none w-full font-medium"
          />
          <button
            onClick={handleSend}
            className="px-4 py-2 rounded-3xl hover:text-white bg-white/80 backdrop-blur-md text-[#000] shadow-md hover:bg-white/30 transition font-medium"
          >
            Go
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatUI;
