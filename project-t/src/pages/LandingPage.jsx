import React from "react";
import { Link } from "react-router-dom";

export default function LandingPage() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-[#fdf6e3] via-[#f9e4d4] to-[#e4c1f9] text-gray-800 font-sans">
      {/* Hero Section */}
      <section className="w-full px-6 md:px-20 py-20 flex flex-col items-center text-center">
        <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-6">
          Discover Your Perfect Trip with <span className="text-[#6a0dad]">TravelMate</span>
        </h1>
        <p className="text-lg md:text-xl max-w-2xl mb-10">
          Tell us where you want to go, how many days, and your interests. Our AI powered by Gemini will help you plan the perfect itinerary — plus connect you with local vendors.
        </p>
        <div className="flex gap-4">
          <Link
            to="/chat"
            className="px-6 py-3 bg-[#6a0dad] text-white rounded-full shadow-lg hover:bg-[#5a0cb5] transition"
          >
            Start Chat
          </Link>
          <Link
            to="/vendor"
            className="px-6 py-3 bg-white text-[#6a0dad] border border-[#6a0dad] rounded-full shadow-lg hover:bg-[#f3e8ff] transition"
          >
            Add Vendor
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 md:px-20 py-16 bg-white/70 backdrop-blur-md">
        <h2 className="text-3xl font-semibold text-center mb-10">What We Offer</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
          <div className="p-6 bg-white rounded-xl shadow-lg">
            <h3 className="text-xl font-semibold mb-2">AI-Powered Planning</h3>
            <p>
              Just tell us your destination and duration — our Gemini AI crafts your trip plan with daily tips and ideas.
            </p>
          </div>
          <div className="p-6 bg-white rounded-xl shadow-lg">
            <h3 className="text-xl font-semibold mb-2">Local Vendor Discovery</h3>
            <p>
              View and connect with local drivers, restaurants, and artisans based on your destination and preferences.
            </p>
          </div>
          <div className="p-6 bg-white rounded-xl shadow-lg">
            <h3 className="text-xl font-semibold mb-2">Easy Vendor Onboarding</h3>
            <p>
              Vendors can quickly submit their details and appear in our smart itinerary suggestions for travelers.
            </p>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="px-6 md:px-20 py-20 text-center bg-[#fdf6e3]">
        <h2 className="text-3xl font-bold mb-6">
          Ready to plan your journey?
        </h2>
        <p className="mb-8 max-w-xl mx-auto">
          Whether you're a traveler or a vendor, TravelMate is here to connect experiences and opportunities.
        </p>
        <Link
          to="/chat"
          className="px-8 py-4 bg-[#6a0dad] text-white rounded-full text-lg font-medium shadow-md hover:bg-[#5a0cb5] transition"
        >
          Chat with TravelMate
        </Link>
      </section>

      {/* Footer */}
      <footer className="text-center py-6 bg-white/50 text-sm">
        &copy; {new Date().getFullYear()} TravelMate. Built with ❤️ and Gemini API.
      </footer>
    </div>
  );
}
