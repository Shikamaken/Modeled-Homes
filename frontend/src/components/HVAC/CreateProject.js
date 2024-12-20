import React, { useState } from 'react';
import { createProject } from '../../utils/api';

const CreateProject = () => {
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const projectData = { name, location };
    try {
      const project = await createProject(projectData);
      console.log('Project created:', project);
      // Clear form or show success message
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Project Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      <input
        type="text"
        placeholder="Project Location"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        required
      />
      <button type="submit">Create Project</button>
    </form>
  );
};

export default CreateProject;
