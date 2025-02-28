// frontend/src/components/HVAC/DesignSuite.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useSelector } from "react-redux";
import { toast } from "react-toastify";
import PDFPageSelector from "./PDFPageSelector";
import FloorPlanRegionSelector from "./FloorPlanRegionSelector";

export default function DesignSuite() {
  const token = useSelector((state) => state.hvac.token);
  const uuid = useSelector((state) => state.hvac.uuid);

  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [buildingPlan, setBuildingPlan] = useState(null);
  const [progress, setProgress] = useState(null);

  const [selectedPage, setSelectedPage] = useState(null);
  const [selectedRegion, setSelectedRegion] = useState(null);

  // ✅ Fetch projects for the user
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const { data } = await axios.get(`http://localhost:4000/api/projects/user/${uuid}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProjects(data.projects);
      } catch (err) {
        console.error("Error fetching projects:", err);
        toast.error("Failed to load projects.");
      }
    };

    fetchProjects();
  }, [token, uuid]);

  // ✅ Handle PDF upload
  const handlePdfUpload = async () => {
    if (!buildingPlan || !selectedProject) {
      toast.error("Please select a project and upload a PDF.");
      return;
    }

    const planId = buildingPlan.name.replace(/\.[^/.]+$/, "");
    const formData = new FormData();
    formData.append("pdf", buildingPlan);
    formData.append("plan_id", planId);
    formData.append("uuid", uuid);

    try {
      // Upload the PDF
      await axios.post(`http://localhost:4000/api/projects/upload/${selectedProject._id}`, formData, {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Start pipeline
      const { data } = await axios.post(
        "http://localhost:4000/api/pipeline/start",
        { uuid, plan_id: planId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.info("Analyzing blueprints...");
      pollProgress(data.projectId);
    } catch (err) {
      console.error("Upload error:", err);
      toast.error("Failed to upload PDF.");
    }
  };

  // ✅ Poll pipeline progress
  const pollProgress = (projectId) => {
    const interval = setInterval(async () => {
      try {
        const { data } = await axios.get(
          `http://localhost:4000/api/pipeline/progress/${projectId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setProgress(data.progress);
        if (data.progress === 100) {
          clearInterval(interval);
          toast.success("Blueprint analysis complete!");
        }
      } catch (err) {
        console.error("Polling error:", err);
        clearInterval(interval);
      }
    }, 2000); // Poll every 2 seconds
  };

  return (
    <div className="p-8">
      <h2 className="text-3xl font-bold mb-6">Design Suite</h2>

      {/* ✅ Project Selection */}
      <div className="mb-6">
        <label className="block font-semibold mb-2">Select a Project:</label>
        <select
          value={selectedProject?._id || ""}
          onChange={(e) =>
            setSelectedProject(projects.find((p) => p._id === e.target.value) || null)
          }
          className="w-full p-2 border rounded"
        >
          <option value="" disabled>Select a project...</option>
          {projects.map((project) => (
            <option key={project._id} value={project._id}>
              {project.projectName}
            </option>
          ))}
        </select>
      </div>

      {/* ✅ PDF Upload */}
      <div className="mb-6">
        <label className="block font-semibold mb-2">Upload Building Plan (PDF):</label>
        <input type="file" accept=".pdf" onChange={(e) => setBuildingPlan(e.target.files[0])} />
        <button
          onClick={handlePdfUpload}
          className="mt-4 bg-[#080653] text-white py-2 px-6 rounded-full font-bold"
          disabled={!buildingPlan || !selectedProject}
        >
          Upload & Analyze
        </button>
      </div>

      {/* ✅ Progress Bar */}
      {progress !== null && (
        <div className="mt-4">
          <p className="text-center font-medium">Analyzing Blueprints ({progress}%)</p>
          <div className="w-full bg-gray-200 rounded-full h-4 mt-2">
            <div
              className="bg-[#080653] h-4 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* ✅ PDF Page Selection */}
      {progress === 100 && !selectedPage && (
        <PDFPageSelector
          pdfUrl={`/uploads/${uuid}/projects/${buildingPlan.name.replace(/\.[^/.]+$/, "")}/${buildingPlan.name}`}
          onPagesSelected={setSelectedPage}
        />
      )}

      {/* ✅ Floor Plan Region Selection */}
      {selectedPage && !selectedRegion && (
        <FloorPlanRegionSelector
          pdfUrl={`/uploads/${uuid}/projects/${buildingPlan.name.replace(/\.[^/.]+$/, "")}/${buildingPlan.name}`}
          selectedPage={selectedPage}
          onRegionSelected={setSelectedRegion}
        />
      )}

      {/* ✅ Selection Summary */}
      {selectedRegion && (
        <div className="mt-6 bg-white text-[#080653] p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Selection Summary</h3>
          <p><strong>Selected Page:</strong> {selectedPage}</p>
          <p><strong>Region Coordinates:</strong> {JSON.stringify(selectedRegion)}</p>
        </div>
      )}
    </div>
  );
}