import React from "react";

const ResponseSection = ({ creativeUrl }) => (
  <div className="response-section">
    <h2>Response</h2>
    <img src={creativeUrl} alt="Generated Creative" style={{ maxWidth: "100%" }} />
  </div>
);

export default ResponseSection;