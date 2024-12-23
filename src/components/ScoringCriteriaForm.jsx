import React from "react";

const ScoringCriteriaForm = ({ formData, handleCriteriaChange }) => (
  <div className="form-section">
    <h2>Scoring Criteria</h2>
    {formData.scoring_criteria.map((criterion) => (
      <label key={criterion}>
        <input
          type="checkbox"
          value={criterion}
          checked={formData.selectedCriteria.includes(criterion)}
          onChange={handleCriteriaChange}
        />
        {criterion}
      </label>
    ))}
  </div>
);

export default ScoringCriteriaForm;
