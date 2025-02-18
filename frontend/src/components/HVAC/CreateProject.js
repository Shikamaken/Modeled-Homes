import React from 'react';
import { useState } from "react";

export default function CreateProject({ onSelectProject }) {
  const [projectName, setProjectName] = useState("");
  const [projectLocation, setProjectLocation] = useState("");

  const handleCreateProject = async () => {
    if (!projectName.trim()) {
      alert("Please enter a project name.");
      return;
    }

    const newProject = {
      name: projectName,
      location: projectLocation,
    };

    try {
      const response = await fetch("http://localhost:4000/api/projects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newProject),
      });

      if (!response.ok) {
        throw new Error("Failed to create project");
      }

      const projectData = await response.json();
      onSelectProject(projectData);

      // Reset fields
      setProjectName("");
      setProjectLocation("");
    } catch (error) {
      console.error("Error creating project:", error);
    }
  };

  return (
    <div className="flex flex-col p-4 border border-gray-300 rounded">
      <h2 className="text-lg font-bold mb-2">Create New Project</h2>
      <input
        type="text"
        placeholder="Project Name"
        value={projectName}
        onChange={(e) => setProjectName(e.target.value)}
        className="p-2 border rounded mb-2"
      />
      <input
        type="text"
        placeholder="Project Location"
        value={projectLocation}
        onChange={(e) => setProjectLocation(e.target.value)}
        className="p-2 border rounded mb-2"
      />
      <button
        onClick={handleCreateProject}
        className="p-2 bg-blue-500 text-white rounded"
      >
        Create Project
      </button>
    </div>
  );
}