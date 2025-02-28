// frontend/src/components/HVAC/SmartSearchField.jsx
import React from "react";

export default function SmartSearchField({
  label,
  searchValue,
  setSearchValue,
  selectedOption,
  setSelectedOption,
  options = [],
  onAdd,
  addButtonLabel = "Add",
  ariaLabel = "Add new",
}) {
    
  const safeOptions = Array.isArray(options) ? options : [];

  console.log("🔎 Options received for search:", safeOptions);

  return (
    <div className="w-full space-y-2">
      <label className="block font-semibold text-sm text-gray-700">
        {label}
      </label>
      <input
        type="text"
        value={searchValue}
        onChange={(e) => setSearchValue(e.target.value)}
        placeholder={`Search ${label.toLowerCase()}...`}
        className="w-full bg-[#E8E8E8] p-3 rounded-md placeholder-gray-500"
        aria-label={`Search ${label}`}
      />
      {options.length > 0 && (
        <ul className="w-full max-h-40 overflow-y-auto border rounded-md">
          {safeOptions.map((option, index) => (
            <li
              key={option._id ?? `${option.username}-${index}`}
              className={`p-2 cursor-pointer ${
                selectedOption?._id === option._id ? "bg-blue-100" : "hover:bg-gray-100"
              }`}
              onClick={() => {
                console.log("🖱 Clicked on:", option);
                if (setSelectedOption) {
                  console.log("✅ Calling setSelectedOption with:", option);
                  setSelectedOption({ ...option });  // ✅ Force state update with a new object
                } else {
                  console.error("❌ setSelectedOption is undefined!");
                }
              }}
            >
              {option.username || option.name || `${option.addressLine1}, ${option.city}`}
            </li>
          ))}
        </ul>
      )}
      <div className="flex justify-between items-center">
        {selectedOption && (
          <span className="text-sm text-green-600">
            Selected: {selectedOption.username || selectedOption.name || selectedOption.addressLine1 || "Unknown"}
          </span>
        )}
        {onAdd && (
          <button
            type="button"
            onClick={onAdd}
            className="bg-[#080653] text-white px-3 py-1 rounded-[20px] text-sm"
            aria-label={ariaLabel}
          >
            {addButtonLabel}
          </button>
        )}
      </div>
    </div>
  );
}