// frontend/src/components/HVAC/AddClientModal.jsx
import React, { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { useSelector } from "react-redux";

export default function AddClientModal({ onSave, onClose }) {
  const [clientName, setClientName] = useState("");
  const { token } = useSelector((state) => state.user); // ✅ Access token from Redux store

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!clientName.trim()) {
      toast.error("Client name cannot be empty.");
      return;
    }

    if (!token) {
      console.error("🚫 Token is undefined.");
      toast.error("Authentication token not found. Please log in again.");
      return;
    }

    try {
      const { data } = await axios.post(
        "http://localhost:4000/api/clients",
        { name: clientName },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (data) {
        console.log("✅ Client added successfully", data);
        console.log("📤 Passing client back to parent component:", data.client);

        toast.success("Client added successfully!");
        onSave(data.client); // ✅ Notify parent component with new client
        onClose();
      } else {
        console.warn("⚠️ No data returned from the server.");
        toast.error("No response from server. Try again later.");
      }
    } catch (err) {
      console.error("🚫 Error adding client:", err);
      toast.error("Failed to add client. Please try again.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="text"
        value={clientName}
        onChange={(e) => setClientName(e.target.value)}
        placeholder="Enter client name"
        className="w-full p-2 border rounded"
        required
      />
      <div className="flex justify-end space-x-2">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Add Client
        </button>
      </div>
    </form>
  );
}