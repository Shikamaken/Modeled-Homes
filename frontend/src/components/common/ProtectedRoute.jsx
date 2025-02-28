// frontend/components/common/ProtectedRoute.jsx
import React from "react";
import { useSelector } from "react-redux";
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children }) {
  const token = useSelector((state) => state.user.token);
  
  console.log("ProtectedRoute - token:", token);

  return token ? children : <Navigate to="/" replace />;
}