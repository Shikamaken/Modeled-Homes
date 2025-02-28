// frontend/src/components/HVAC/AddLocationModal.jsx
import React, { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { useSelector } from "react-redux";

export default function AddLocationModal({ onClose, onSave, clientId }) {
  const { token } = useSelector((state) => state.user);  // ✅ Access token
  const [addressLine1, setAddressLine1] = useState("");
  const [addressLine2, setAddressLine2] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [zip, setZip] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    console.log("🚀 Submitting location with:", {
      clientId,
      addressLine1,
      addressLine2,
      city,
      state,
      zip,
    });

    try {
      const { data } = await axios.post(
        "http://localhost:4000/api/locations",
        { clientId, addressLine1, addressLine2, city, state, zip },
        { headers: { Authorization: `Bearer ${token}` } }  // ✅ Add token here
      );

      toast.success("Location added successfully!");
      onSave(data);  // ✅ Pass to parent
      onClose();
    } catch (err) {
      console.error("🚫 Error adding location:", err);
      toast.error("Failed to add location.");
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-header">Add New Location</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Address Line 1"
            value={addressLine1}
            onChange={(e) => setAddressLine1(e.target.value)}
            required
            className="modal-input"
          />
          <input
            type="text"
            placeholder="Address Line 2"
            value={addressLine2}
            onChange={(e) => setAddressLine2(e.target.value)}
            className="modal-input"
          />
          <input
            type="text"
            placeholder="City"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            required
            className="modal-input"
          />
          <input
            type="text"
            placeholder="State"
            value={state}
            onChange={(e) => setState(e.target.value)}
            required
            className="modal-input"
          />
          <input
            type="text"
            placeholder="ZIP Code"
            value={zip}
            onChange={(e) => setZip(e.target.value)}
            required
            className="modal-input"
          />
          <button type="submit" className="modal-button">
            Add Location
          </button>
        </form>
        <button onClick={onClose} className="modal-close">Close</button>
      </div>
    </div>
  );
}