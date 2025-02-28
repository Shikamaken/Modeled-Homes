// frontend/src/components/HVAC/UserHome.jsx
import React, { useState } from "react";
import NewProjectPopup from "./NewProjectPopup";

export default function UserHome() {
  const [showNewProject, setShowNewProject] = useState(false);

  // Mock data for Recently Viewed projects
  const recentProjects = [
    { name: "Sample Floor Plan 1", client: "Acme Builders", lastViewed: "2024-02-23" },
    { name: "Modern Loft Renovation", client: "Urban Homes", lastViewed: "2024-02-22" },
    { name: "Redacted Plan", client: "Confidential", lastViewed: "2024-02-21" },
  ];

  return (
    <div className="min-h-screen bg-[#080653] text-white relative">
      {/* Top-right buttons */}
      <div className="absolute top-4 right-4 flex space-x-4">
        <button
          onClick={() => alert("Add Account functionality coming soon!")}
          className="bg-white text-[#080653] px-4 py-2 rounded-full font-semibold hover:bg-gray-200"
          aria-label="Add Account"
        >
          Add Account
        </button>
        <button
          onClick={() => setShowNewProject(true)}
          className="bg-[#FF6B6B] text-white px-4 py-2 rounded-full font-semibold hover:bg-red-500"
          aria-label="New Project"
        >
          New Project
        </button>
      </div>

      {/* Header */}
      <div className="pt-20 text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to Modeled Homes</h1>
        <p className="text-lg">Manage your projects and streamline your workflow.</p>
      </div>

      {/* Recently Viewed */}
      <div className="max-w-4xl mx-auto mt-12 bg-white text-[#080653] rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">Recently Viewed</h2>
        {recentProjects.length > 0 ? (
          <table className="w-full text-left">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-2 px-4">Project Name</th>
                <th className="py-2 px-4">Client</th>
                <th className="py-2 px-4">Last Viewed</th>
              </tr>
            </thead>
            <tbody>
              {recentProjects.map((project, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="py-2 px-4">{project.name}</td>
                  <td className="py-2 px-4">{project.client}</td>
                  <td className="py-2 px-4">{project.lastViewed}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No recent projects found.</p>
        )}
      </div>

      {/* New Project Popup */}
      {showNewProject && <NewProjectPopup onClose={() => setShowNewProject(false)} />}
    </div>
  );
}