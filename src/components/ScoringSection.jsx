import React from "react";

const ScoringSection = ({ scoring }) => (
  <div className="response-section">
    <h2>Scoring</h2>
    <ul>
      {Object.entries(scoring).map(([key, value]) => (
        <li key={key}>
          {key}: {value}
        </li>
      ))}
    </ul>
  </div>
);

export default ScoringSection;
