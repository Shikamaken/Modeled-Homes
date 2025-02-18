import React from 'react';
import { Routes, Route, Link } from "react-router-dom";
import DesignSuite from "./components/HVAC/DesignSuite";
import Home from "./components/Home";

function App() {
  return (
    <div className="flex flex-col items-center p-4">
      <h1 className="text-xl font-bold mb-4">Modeled Homes</h1>
      <nav>
        <ul className="flex space-x-4">
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/design-suite">Design Suite</Link>
          </li>
        </ul>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/design-suite" element={<DesignSuite />} />
      </Routes>
    </div>
  );
}

export default App;