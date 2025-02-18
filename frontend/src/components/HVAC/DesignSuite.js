import React from 'react';
import { useState, useEffect } from "react";

export default function DesignSuite() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);

  useEffect(() => {
    // Fetch projects from the backend when the component loads
    fetch("http://localhost:4000/api/projects")
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setProjects(data); // Ensure we're setting valid data
        } else {
          console.error("Unexpected response format:", data);
        }
      })
      .catch((error) => console.error("Error fetching projects:", error));
  }, []);

  const handleFileUpload = async (event, projectId) => {
    const file = event.target.files[0];
    if (!file) {
      alert("No file selected.");
      return;
    }

    const formData = new FormData();
    formData.append("pdf", file);
    formData.append("projectId", projectId); // ✅ Ensure this is included

    console.log("Uploading PDF with projectId:", projectId); // ✅ Debugging

    try {
      const response = await fetch(`http://localhost:4000/api/projects/upload/${projectId}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to upload PDF. Server response: ${errorText}`);
      }

      alert(`PDF uploaded successfully to project_${projectId}!`);
    } catch (error) {
      console.error("Error uploading PDF:", error);
      alert(`Error uploading PDF: ${error.message}`);
    }
  };
  
  return (
    <div className="flex flex-col items-center p-4">
      <h1 className="text-xl font-bold mb-4">Design Suite Setup</h1>

      {/* Project Selection Dropdown */}
      <select
        className="p-2 border rounded mb-4"
        onChange={(e) => setSelectedProject(JSON.parse(e.target.value))}
      >
        <option value="">Select a Project</option>
        {projects.length > 0 ? (
          projects.map((project) => (
            <option key={project.id} value={JSON.stringify(project)}>
              {project.name}
            </option>
          ))
        ) : (
          <option disabled>No projects found</option>
        )}
      </select>

      {selectedProject && (
        <div className="mt-4">
          <h2 className="text-lg font-bold">{selectedProject.name}</h2>
          <p>Location: {selectedProject.location}</p>
          <p>Project ID: {selectedProject.id}</p>

          {/* PDF Upload Input */}
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => handleFileUpload(e, selectedProject.id)}
            className="mt-4 p-2 border rounded"
          />
        </div>
      )}
    </div>
  );
}