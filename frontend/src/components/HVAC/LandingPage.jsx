// frontend/src/components/HVAC/LandingPage.jsx
import React, { useState } from "react";
import GetStartedPopup from "./GetStartedPopup";
import SignInPopup from "./SignInPopup";

export default function LandingPage() {
  const [showGetStarted, setShowGetStarted] = useState(false);
  const [showSignIn, setShowSignIn] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-[#ECF0F1] text-[#000A2C]">
      {/* Hero Section */}
      <header className="bg-[#000A2C] text-white py-12 border-b-2 border-[#3498DB]">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-5xl font-black leading-tight mb-4">
            Revolutionizing HVAC Design
          </h1>
          <p className="text-2xl font-semibold">
            From Bid to Installation
          </p>
          <p className="text-lg mt-4">
            Modeled HVAC streamlines your entire project – from sketch to startup – 
            with AI-powered automation and AR-driven execution.
          </p>
          <div className="flex justify-center space-x-4 mt-6">
            <button
              onClick={() => setShowGetStarted(true)}
              className="bg-gradient-to-b from-[#3498DB] to-[#1C5175] text-white font-extrabold px-8 py-3 rounded-full hover:opacity-90 transition"
              aria-label="Get Started"
            >
              Get Started
            </button>
            <button
              onClick={() => setShowSignIn(true)}
              className="text-[#0000FF] font-semibold underline"
              aria-label="Sign In"
            >
              Already a member? Sign in here.
            </button>
          </div>
        </div>
      </header>

      {/* Feature Section */}
      <section className="py-16 text-center">
        <h2 className="text-3xl font-semibold mb-8">
          Powerful Tools Made for HVAC Professionals
        </h2>
        <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-10">
          {[
            {
              title: "Building Plan Conversion",
              desc: "Upload blueprints to automatically generate your 2D/3D workspace.",
            },
            {
              title: "Design Suite",
              desc: "Quickly identify obstacles, navigate duct runs, and draft precise bids with unprecedented ease and insight.",
            },
            {
              title: "Field Support",
              desc: "Use on-site AR design visualization to guide accurate installations.",
            },
            {
              title: "Operations Center (Coming Soon)",
              desc: "Model your growth with streamlined administrative workflows built for HVAC businesses of all sizes.",
            },
          ].map(({ title, desc }) => (
            <div key={title} className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold text-xl mb-2">{title}</h3>
              <p className="text-gray-700">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-16 text-center bg-[#000A2C] text-white">
        <h2 className="text-3xl font-semibold">
          Equip your team with the resources to bid faster, plan smarter, and install with precision.
        </h2>
        <p className="text-xl mt-4">
          Join now and experience the future of HVAC design.
        </p>
        <button
          onClick={() => alert("Contact form coming soon!")}
          className="mt-6 bg-gradient-to-b from-[#3498DB] to-[#1C5175] text-white font-bold px-6 py-3 rounded-lg hover:opacity-90 transition"
          aria-label="Request a Demo"
        >
          Request a Demo
        </button>
      </section>

      {/* Footer */}
      <footer className="bg-[#000A2C] text-[#ECF0F1] py-6 text-center border-t-2 border-[#3498DB]">
        <p className="text-lg">&copy; 2025 Modeled Homes. All rights reserved.</p>
        <p className="text-lg mt-2">info@modeledhomes.com | (561) 247-1837</p>
      </footer>

      {/* Popups */}
      {showGetStarted && <GetStartedPopup onClose={() => setShowGetStarted(false)} />}
      {showSignIn && <SignInPopup onClose={() => setShowSignIn(false)} />}
    </div>
  );
}