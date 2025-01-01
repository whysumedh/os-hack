// import React from "react";

// const ScoringSection = ({ scoring }) => (
//   <div className="response-section">
//     <h2>Scoring</h2>
//     <ul>
//       {Object.entries(scoring).map(([key, value]) => (
//         <li key={key}>
//           {key}: {value}
//         </li>
//       ))}
//     </ul>
//   </div>
// );

// export default ScoringSection;


import React from "react";

const ScoringSection = ({ scoring, fileSize, dimensions}) => (
  <div className="response-section">
    <h2>Scoring</h2>
    <ul>
      {Object.entries(scoring).map(([key, value]) => (
        <li key={key}>
          {key}: {value}
        </li>
      ))}
      <li>File Size: {fileSize} KB</li>
      <li>Dimensions: {dimensions.width} X {dimensions.height} pixels</li>
    </ul>
  </div>
);

export default ScoringSection;
