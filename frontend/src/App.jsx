// frontend/src/App.jsx
import React from 'react';
import { Routes, Route } from "react-router-dom";
import ProtectedRoute from "./components/common/ProtectedRoute";
import LandingPage from "./components/HVAC/LandingPage";
import UserHome from "./components/HVAC/UserHome";
import DesignSuite from "./components/HVAC/DesignSuite";
import Navbar from "./components/common/Navbar";
import "./App.css";

function App() {
  return (
    <div className="flex flex-col items-center p-4">
      <h1 className="text-xl font-bold mb-4">Modeled Homes</h1>
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route
          path="/account-home"
          element={
            <ProtectedRoute>
              <UserHome />
            </ProtectedRoute>
          }
        />
        <Route
          path="/design-suite"
          element={
            <ProtectedRoute>
              <DesignSuite />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}

export default App;