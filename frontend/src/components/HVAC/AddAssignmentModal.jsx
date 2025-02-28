// frontend/src/components/HVAC/AddAssignmentModal.jsx
import React, { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { useSelector } from "react-redux";

export default function AddAssignmentModal({ onClose, onSave }) {
  const { token } = useSelector((state) => state.user);
  const [name, setName] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    console.log("🚀 Sending request to add user/team:", { name });

    try {
      const { data } = await axios.post(
        "http://localhost:4000/api/users", 
        { name },
        { headers: { Authorization: `Bearer ${token}` } }  // ✅ Add token here
      );
      
      console.log("✅ User/Team added successfully:", data);

      toast.success("User/Team added successfully!");
      onSave(data); // Pass the new assignment to the parent component
      onClose();
    } catch (err) {
      console.error("Error adding user/team:", err);
      toast.error("Failed to add user/team.");
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-header">Add User or Team</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="modal-input"
          />
          <button type="submit" className="modal-button">
            Add Assignment
          </button>
        </form>
        <button onClick={onClose} className="modal-close">Close</button>
      </div>
    </div>
  );
}