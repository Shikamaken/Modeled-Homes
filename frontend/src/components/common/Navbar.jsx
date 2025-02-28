// frontend/src/components/common/Navbar.jsx
import React from "react";
import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();

  // Hide navbar on the landing page
  if (pathname === "/") return null;

  return (
    <nav className="flex justify-between items-center p-4 bg-gray-800 text-white">
      <Link to="/account-home" className="font-bold text-lg">Account Home</Link>
      <Link
        to="#"
        className="font-bold text-lg"
        onClick={(e) => {
          e.preventDefault(); // 🚫 Prevents navigation
          alert("Design Suite functionality coming soon!");
        }}
      >
        Design Suite
      </Link>
    </nav>
  );
}