// components/common/SmartSearchField.jsx
import React, { useState } from "react";

export default function SmartSearchField({
  label,
  searchValue,
  setSearchValue,
  options = [],
  selectedOption,
  setSelectedOption,
  addButtonLabel,
  ariaLabel,
}) {
  const [showDropdown, setShowDropdown] = useState(false);

  const handleInputChange = (e) => {
    setSearchValue(e.target.value);
    setShowDropdown(true);
  };

  const handleOptionClick = (option) => {
    setSelectedOption(option); // ✅ Update selected option
    setSearchValue(option.name ?? option.addressLine1); // ✅ Update input text
    setShowDropdown(false); // ✅ Close dropdown after selection
  };

  const handleAddNew = () => {
    alert("Add new functionality coming soon!");
  };

  return (
    <div className="relative w-full">
      <label className="block font-medium mb-1">{label}</label>
      <div className="flex items-center space-x-2">
        <input
          type="text"
          value={searchValue}
          onChange={handleInputChange}
          placeholder={`Search ${label.toLowerCase()}...`}
          className="w-full bg-[#E8E8E8] p-3 rounded-md placeholder-gray-500"
          aria-label={ariaLabel}
          onFocus={() => setShowDropdown(true)}
        />
        <button
          onClick={handleAddNew}
          className="bg-blue-600 text-white px-3 py-2 rounded-md text-sm"
          aria-label={ariaLabel}
        >
          {addButtonLabel}
        </button>
      </div>
      {showDropdown && options.length > 0 && (
        <ul className="absolute z-10 w-full mt-1 border rounded-md bg-white shadow-md max-h-48 overflow-y-auto">
          {options.map((option) => (
            <li
              key={option._id}
              className="p-2 hover:bg-gray-100 cursor-pointer"
              onClick={() => handleOptionClick(option)}
            >
              {option.name || `${option.addressLine1 ?? "Unknown"}, ${option.city ?? "N/A"}`}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}