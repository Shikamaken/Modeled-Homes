// frontend/src/components/HVAC/GetStartedPopup.jsx
import React, { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { setUser } from "../../reducers/hvacReducer";

export default function GetStartedPopup({ onClose }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", phone: "", password: "" });
  const dispatch = useDispatch();
  
  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await axios.post("http://localhost:4000/api/auth/register", form); // ✅ Destructure response
      dispatch(setUser({ token: data.token, uuid: data.uuid }));
      toast.success("Account created successfully!");
      onClose();
      navigate("/account-home"); // ✅ Now works properly
    } catch (err) {
      console.error("Registration failed:", err);
      toast.error("Registration failed. Please check your details and try again.");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-[25px] border border-black w-[534px] p-8 shadow-lg">
        <h2 className="text-2xl font-bold mb-4 text-center">Get Started</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {["username", "email", "phone", "password"].map((field) => (
            <input
              key={field}
              type={field === "password" ? "password" : field === "email" ? "email" : "text"}
              name={field}
              value={form[field]}
              onChange={handleChange}
              placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
              className="w-full bg-[#E8E8E8] p-3 rounded-md placeholder-gray-500"
              aria-label={field}
              required
            />
          ))}
          <button
            type="submit"
            className="w-full bg-[#080653] text-white py-2 rounded-[25px] font-bold text-lg"
          >
            Create Account
          </button>
        </form>
        <button
          onClick={onClose}
          className="mt-4 w-full text-center text-[#080653] font-semibold hover:underline"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}