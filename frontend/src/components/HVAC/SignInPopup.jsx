// frontend/src/components/HVAC/SignInPopup.jsx
import React, { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { setUser } from "../../reducers/hvacReducer";

export default function SignInPopup({ onClose }) {
  const [form, setForm] = useState({ username: "", password: "" });
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const dispatch = useDispatch();

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Submitting login form:", form);
    
    try {
      const { data } = await axios.post("http://localhost:4000/api/auth/login", form, {
        headers: { "Content-Type": "application/json" },
      });

      console.log("Login response:", data); // ✅ See response from backend

      dispatch(setUser({ token: data.token, uuid: data.uuid }));
      console.log("🚀 Dispatched setUser with:", { token: data.token, uuid: data.uuid });
      toast.success("Signed in successfully!");

      onClose();
      navigate("/account-home");
    } catch (err) {
      console.error("Login error:", err.response?.data || err.message); // ✅ Check error details
      toast.error("Login failed. Please check your credentials.");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-[25px] border border-black w-[534px] p-8 shadow-lg">
        <h2 className="text-2xl font-bold mb-4 text-center">Sign In</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {["username", "password"].map((field) => (
            <input
              key={field}
              type={field}
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
            Sign In
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