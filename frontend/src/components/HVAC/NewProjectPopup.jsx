// frontend/src/components/HVAC/NewProjectPopup.jsx
import React, { useState, useEffect, useCallback } from "react";
import { useSelector } from "react-redux";
import axios from "axios";
import { toast } from "react-toastify";
import SmartSearchField from "./SmartSearchField";
import AddClientModal from "./AddClientModal";
import AddLocationModal from "./AddLocationModal";
import PDFPageSelectorImage from "./PDFPageSelectorImage";

export default function NewProjectPopup({ onClose }) {
  const { token, uuid, user } = useSelector((state) => state.user);

  // Form state
  const [projectName, setProjectName] = useState("");
  const [clientSearch, setClientSearch] = useState("");
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [locationSearch, setLocationSearch] = useState("");
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [assignmentSearch, setAssignmentSearch] = useState("");
  const [assignments, setAssignments] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [buildingPlan, setBuildingPlan] = useState(null);

  // Modal state
  const [showAddClientModal, setShowAddClientModal] = useState(false);
  const [showAddLocationModal, setShowAddLocationModal] = useState(false);

  // Control whether PDFPageSelectorImage is rendered
  const [showPdfSelector, setShowPdfSelector] = useState(false);

  const handleClientCreated = (newClient) => {
    setClients((prev) => [...prev, newClient]);
    setSelectedClient(newClient);
    setShowAddClientModal(false);
  };

  const handleLocationCreated = (newLocation) => {
    setLocations((prev) => [...prev, newLocation]);
    setSelectedLocation(newLocation);
    setShowAddLocationModal(false);
  };

  const fetchData = useCallback(async (endpoint, setter, searchValue, clientId = null) => {
    try {
      const params = { query: searchValue };
      if (endpoint === "locations" && clientId) {
        params.clientId = clientId;
      }
      const apiUrl = `http://localhost:4000/api/${endpoint}/search`;
      const headers = { Authorization: `Bearer ${token}` };
      const { data } = await axios.get(apiUrl, { params, headers });
      if (endpoint === "clients") {
        setter(data.clients ?? []);
      } else if (endpoint === "locations") {
        setter(data.locations ?? []);
      } else if (endpoint === "users") {
        setter(data.users ?? []);
      }
    } catch (err) {
      console.error(`Error fetching ${endpoint}:`, err.response?.data || err);
    }
  }, [token]);

  useEffect(() => {
    if (clientSearch.trim()) fetchData("clients", setClients, clientSearch);
    if (locationSearch.trim() && selectedClient) {
      fetchData("locations", setLocations, locationSearch, selectedClient._id);
    }
    if (assignmentSearch.trim()) fetchData("users", setAssignments, assignmentSearch);
  }, [clientSearch, locationSearch, assignmentSearch, selectedClient, fetchData]);

  const handleStartProject = async () => {
    if (!projectName.trim() || !selectedClient || !selectedLocation || !buildingPlan) {
      toast.error("Please complete all required fields.");
      return;
    }
    const planId = buildingPlan.name.replace(/\.[^/.]+$/, "");
    try {
      await axios.post("http://localhost:4000/api/projects/create", {
        projectName,
        clientId: selectedClient._id,
        locationId: selectedLocation._id,
        assignedUser: selectedAssignment ? selectedAssignment._id : uuid,
        uuid,
        plan_id: planId,
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      const formData = new FormData();
      formData.append("pdf", buildingPlan);
      const uploadUrl = "http://localhost:4000/api/projects/upload";
      await axios.post(uploadUrl, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          uuid: user.uuid,
          plan_id: planId,
        },
      });
      toast.success("PDF uploaded! Processing, please wait...");
      // Trigger PDFPageSelectorImage; it will handle polling and display internally.
      setShowPdfSelector(true);
    } catch (err) {
      console.error("Error starting project:", err);
      toast.error("Failed to start project.");
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg w-[534px]">
      <h2 className="text-xl font-bold mb-4">New Project</h2>
      <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); handleStartProject(); }}>
        <input
          type="text"
          placeholder="Project Name*"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          className="w-full bg-gray-200 p-3 rounded-md placeholder-gray-500"
          required
        />
        <SmartSearchField
          label="Client*"
          searchValue={clientSearch}
          setSearchValue={setClientSearch}
          options={clients ?? []}
          selectedOption={selectedClient}
          setSelectedOption={setSelectedClient}
          addButtonLabel="Add Client"
          ariaLabel="Add new client"
          onAdd={() => setShowAddClientModal(true)}
        />
        {selectedClient && (
          <SmartSearchField
            label="Location*"
            searchValue={locationSearch}
            setSearchValue={setLocationSearch}
            options={locations ?? []}
            selectedOption={selectedLocation}
            setSelectedOption={setSelectedLocation}
            addButtonLabel="Add Location"
            ariaLabel="Add new location"
            onAdd={() => setShowAddLocationModal(true)}
          />
        )}
        <SmartSearchField
          label="Assignment"
          searchValue={assignmentSearch}
          setSearchValue={setAssignmentSearch}
          options={assignments ?? []}
          selectedOption={selectedAssignment}
          setSelectedOption={setSelectedAssignment}
        />
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setBuildingPlan(e.target.files[0])}
          className="w-full bg-gray-200 p-3 rounded-md placeholder-gray-500"
          required
        />
        <button
          type="submit"
          className="w-full bg-[#080653] text-white py-2 rounded-[25px] font-bold text-lg disabled:opacity-50"
          disabled={!projectName.trim() || !selectedClient || !selectedLocation || !buildingPlan}
        >
          Start Project
        </button>
      </form>
      {showAddClientModal && (
        <AddClientModal
          isOpen={showAddClientModal}
          onClose={() => setShowAddClientModal(false)}
          onSave={handleClientCreated}
        />
      )}
      {showAddLocationModal && (
        <AddLocationModal
          isOpen={showAddLocationModal}
          onClose={() => setShowAddLocationModal(false)}
          onSave={handleLocationCreated}
          clientId={selectedClient?._id}
        />
      )}
      {showPdfSelector && buildingPlan && (
        <PDFPageSelectorImage 
          uuid={uuid}
          planId={buildingPlan.name.replace(/\.[^/.]+$/, "")}
          buildingPlan={buildingPlan}
          token={token}
          onRegionSelected={({ region, pageIndex }) => {
            console.log("Final PDF region (in PDF coordinates):", region);
            console.log("Selected page index (0-based):", pageIndex);
            // Apply to line detection results 
            // Complete wall identification
            // Transition to Design Suite
          }}
        />
      )}
    </div>
  );
}