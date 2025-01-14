// import React, { useState } from "react";
// import CreativeDetailsForm from "../components/CreativeDetailsForm";
// import ScoringCriteriaForm from "../components/ScoringCriteriaForm";
// import ResponseSection from "../components/ResponseSection";
// import ScoringSection from "../components/ScoringSection";
// import "../styles.css";

// const Form = () => {
//   const [formData, setFormData] = useState({
//     product_name: "",
//     tagline: "",
//     brand_palette: ["#FFC107", "#212121", "#FFFFFF"],
//     width: 1024,
//     height: 1024,
//     cta_text: "",
//     logo_url: "",
//     product_image_url: "",
//     scoring_criteria: [
//       "Background-Foreground Separation",
//       "Brand Guideline Adherence",
//       "Creativity Visual Appeal",
//       "Product Focus",
//       "Call to Action",
//     ],
//     selectedCriteria: [],
//   });

//   const [responseData, setResponseData] = useState(null);
//   const [loading, setLoading] = useState(false); // Add loading state

//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setFormData({ ...formData, [name]: value });
//   };

//   const handleArrayChange = (index, value) => {
//     const updatedPalette = [...formData.brand_palette];
//     updatedPalette[index] = value;
//     setFormData({ ...formData, brand_palette: updatedPalette });
//   };

//   const handleCriteriaChange = (e) => {
//     const { value, checked } = e.target;
//     const updatedCriteria = checked
//       ? [...formData.selectedCriteria, value]
//       : formData.selectedCriteria.filter((item) => item !== value);
//     setFormData({ ...formData, selectedCriteria: updatedCriteria });
//   };

//   const calculateScores = () => {
//     const totalSelected = formData.selectedCriteria.length;
//     const scorePerCriterion = totalSelected > 0 ? 100 / totalSelected : 0;

//     return formData.selectedCriteria.reduce((scores, criterion) => {
//       scores[criterion] = scorePerCriterion;
//       return scores;
//     }, {});
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setLoading(true); // Show loading spinner

//     const scoringCriteria = calculateScores();

//     const requestBody = {
//       creative_details: {
//         product_name: formData.product_name,
//         tagline: formData.tagline,
//         brand_palette: formData.brand_palette,
//         dimensions: {
//           width: formData.width,
//           height: formData.height,
//         },
//         cta_text: formData.cta_text,
//         logo_url: formData.logo_url,
//         product_image_url: formData.product_image_url,
//       },
//       scoring_criteria: scoringCriteria,
//     };

//     console.log("Request JSON:", JSON.stringify(requestBody, null, 2));

//     try {
//       const response = await fetch(
//         "https://creative-api-141459457956.us-central1.run.app/generate_creative",
//         {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify(requestBody),
//         }
//       );
//       const data = await response.json();
//       setResponseData(data);
//     } catch (error) {
//       console.error("Error fetching creative:", error);
//     } finally {
//       setLoading(false); // Hide loading spinner
//     }
//   };

//   return (
//     <div>
//       <form onSubmit={handleSubmit}>
//         <div className="form-sections">
//           <CreativeDetailsForm
//             formData={formData}
//             handleInputChange={handleInputChange}
//             handleArrayChange={handleArrayChange}
//           />
//           <ScoringCriteriaForm
//             formData={formData}
//             handleCriteriaChange={handleCriteriaChange}
//           />
//         </div>
//         <button type="submit" disabled={loading}>
//           {loading ? "Submitting..." : "Submit"}
//         </button>
//       </form>

//       {loading && (
//         <div className="loading-screen">
//           <div className="spinner"></div>
//           <p>Loading...</p>
//         </div>
//       )}

//       {responseData && (
//         <div className="response-container">
//           <ResponseSection creativeUrl={responseData.creative_url} />
//           <ScoringSection scoring={responseData.scoring.scoring} />
//         </div>
//       )}
//     </div>
//   );
// };

// export default Form;
















// import React, { useState } from "react";
// import CreativeDetailsForm from "../components/CreativeDetailsForm";
// import ScoringCriteriaForm from "../components/ScoringCriteriaForm";
// import ResponseSection from "../components/ResponseSection";
// import ScoringSection from "../components/ScoringSection";
// import "../styles.css";

// const Form = () => {
//   const [formData, setFormData] = useState({
//     product_name: "",
//     tagline: "",
//     brand_palette: ["#FFC107", "#212121", "#FFFFFF"],
//     width: 1024,
//     height: 1024,
//     cta_text: "",
//     logo_url: "",
//     product_image_url: "",
//     scoring_criteria: [
//       "Background-Foreground Separation",
//       "Brand Guideline Adherence",
//       "Creativity Visual Appeal",
//       "Product Focus",
//       "Call to Action",
//     ],
//     selectedCriteria: [],
//   });

//   const [responseData, setResponseData] = useState(null);
//   const [loading, setLoading] = useState(false); // Add loading state

//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setFormData({ ...formData, [name]: value });
//   };

//   const handleArrayChange = (index, value) => {
//     const updatedPalette = [...formData.brand_palette];
//     updatedPalette[index] = value;
//     setFormData({ ...formData, brand_palette: updatedPalette });
//   };

//   const handleCriteriaChange = (e) => {
//     const { value, checked } = e.target;
//     const updatedCriteria = checked
//       ? [...formData.selectedCriteria, value]
//       : formData.selectedCriteria.filter((item) => item !== value);
//     setFormData({ ...formData, selectedCriteria: updatedCriteria });
//   };

//   const calculateScores = () => {
//     const totalSelected = formData.selectedCriteria.length;
//     const scorePerCriterion = totalSelected > 0 ? 100 / totalSelected : 0;

//     return formData.selectedCriteria.reduce((scores, criterion) => {
//       scores[criterion] = scorePerCriterion;
//       return scores;
//     }, {});
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setLoading(true); // Show loading spinner

//     const scoringCriteria = calculateScores();

//     const requestBody = {
//       creative_details: {
//         product_name: formData.product_name,
//         tagline: formData.tagline,
//         brand_palette: formData.brand_palette,
//         dimensions: {
//           width: formData.width,
//           height: formData.height,
//         },
//         cta_text: formData.cta_text,
//         logo_url: formData.logo_url,
//         product_image_url: formData.product_image_url,
//       },
//       scoring_criteria: scoringCriteria,
//     };

//     console.log("Request JSON:", JSON.stringify(requestBody, null, 2));

//     try {
//       const response = await fetch(
//         "https://creative-api-141459457956.us-central1.run.app/generate_creative",
//         {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify(requestBody),
//         }
//       );
//       const data = await response.json();
//       setResponseData(data);
//     } catch (error) {
//       console.error("Error fetching creative:", error);
//     } finally {
//       setLoading(false); // Hide loading spinner
//     }
//   };

//   return (
//     <div>
//       <form onSubmit={handleSubmit}>
//         <div className="form-sections">
//           <CreativeDetailsForm
//             formData={formData}
//             handleInputChange={handleInputChange}
//             handleArrayChange={handleArrayChange}
//           />
//           <ScoringCriteriaForm
//             formData={formData}
//             handleCriteriaChange={handleCriteriaChange}
//           />
//         </div>
//         <button type="submit" disabled={loading}>
//           {loading ? "Submitting..." : "Submit"}
//         </button>
//       </form>

//       {loading && (
//         <div className="loading-screen">
//           <div className="spinner"></div>
//           <p>Loading...</p>
//         </div>
//       )}

//       {responseData && (
//         <div className="response-container">
//           <ResponseSection creativeUrl={responseData.creative_url} />
//           <ScoringSection scoring={responseData.scoring.scoring} 
//             fileSize={responseData.metadata.file_size_kb}
//             dimensions={responseData.metadata.dimensions}
//           />
//         </div>
//       )}
//     </div>
//   );
// };

// export default Form;
























import React, { useState } from "react";
import CreativeDetailsForm from "../components/CreativeDetailsForm";
import ScoringCriteriaForm from "../components/ScoringCriteriaForm";
import ResponseSection from "../components/ResponseSection";
import ScoringSection from "../components/ScoringSection";
import "../styles.css";

const Form = () => {
  const [formData, setFormData] = useState({
    product_name: "",
    tagline: "",
    brand_palette: ["#FFC107", "#212121", "#FFFFFF"],
    width: 1024,
    height: 1024,
    cta_text: "",
    logo_url: "",
    product_image_url: "",
    scoring_criteria: [
      "Background-Foreground Separation",
      "Brand Guideline Adherence",
      "Creativity Visual Appeal",
      "Product Focus",
      "Call to Action",
    ],
    selectedCriteria: [],
    newCriteria: "", // Temporary state for adding new criteria
  });

  const [responseData, setResponseData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleArrayChange = (index, value) => {
    const updatedPalette = [...formData.brand_palette];
    updatedPalette[index] = value;
    setFormData({ ...formData, brand_palette: updatedPalette });
  };

  const handleCriteriaChange = (e) => {
    const { value, checked } = e.target;
    const updatedCriteria = checked
      ? [...formData.selectedCriteria, value]
      : formData.selectedCriteria.filter((item) => item !== value);
    setFormData({ ...formData, selectedCriteria: updatedCriteria });
  };

  // Add a new custom scoring criterion
  const addCustomCriteria = () => {
    if (formData.newCriteria.trim()) {
      setFormData({
        ...formData,
        scoring_criteria: [...formData.scoring_criteria, formData.newCriteria],
        newCriteria: "", // Clear the input field
      });
    }
  };

  const calculateScores = () => {
    const totalSelected = formData.selectedCriteria.length;
    if (totalSelected === 0) return {};

    const scorePerCriterion = Math.floor(100 / totalSelected); // Floor division
    const scores = {};

    // Assign the floor value to each criterion
    formData.selectedCriteria.forEach((criterion) => {
      scores[criterion] = scorePerCriterion;
    });

    // Distribute the remaining weight (if any) equally among the criteria
    let remainingScore = 100 - scorePerCriterion * totalSelected;
    for (let i = 0; i < remainingScore; i++) {
      scores[formData.selectedCriteria[i]] += 1;
    }

    return scores;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const scoringCriteria = calculateScores();

    const requestBody = {
      creative_details: {
        product_name: formData.product_name,
        tagline: formData.tagline,
        brand_palette: formData.brand_palette,
        dimensions: {
          width: formData.width,
          height: formData.height,
        },
        cta_text: formData.cta_text,
        logo_url: formData.logo_url,
        product_image_url: formData.product_image_url,
      },
      scoring_criteria: scoringCriteria,
    };

    console.log("Request JSON:", JSON.stringify(requestBody, null, 2));

    try {
      const response = await fetch(
        "https://creative-api-141459457956.us-central1.run.app/generate_creative",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        }
      );
      const data = await response.json();
      setResponseData(data);
    } catch (error) {
      console.error("Error fetching creative:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div className="form-sections">
          <CreativeDetailsForm
            formData={formData}
            handleInputChange={handleInputChange}
            handleArrayChange={handleArrayChange}
          />
          <div className="scoring-criteria" style={{
      backgroundColor: "#f9f9f9"
    }}>
            <ScoringCriteriaForm
              formData={formData}
              handleCriteriaChange={handleCriteriaChange}
            />
            {/* Add custom scoring section inside the scoring criteria */}
            <div
              className="custom-scoring-section"
              style={{ backgroundColor: "#f9f9f9", paddingBottom: "10px" }}
            >
              <h2
                style={{
                  marginLeft: "15px",
                  paddingTop: "10px",
                  marginTop: "2",
                }}
              >
                Add Custom Scoring Criteria
              </h2>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <input
                  type="text"
                  name="newCriteria"
                  value={formData.newCriteria}
                  onChange={(e) => handleInputChange(e)}
                  placeholder="Enter custom criteria"
                  style={{
                    flex: "1",
                    marginLeft: "15px",
                    marginRight: "20px",
                    marginTop: "2",
                  }}
                />
                <button
                  type="button"
                  onClick={addCustomCriteria}
                  style={{
                    padding: "8px 10px",
                    marginRight: "300px",
                    marginTop: 2,
                    color: "#fff",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  Add Criteria
                </button>
              </div>
            </div>
          </div>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit"}
        </button>
      </form>

      {loading && (
        <div className="loading-screen">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      )}

      {responseData && (
        <div className="response-container">
          <ResponseSection creativeUrl={responseData.creative_url} />
          <ScoringSection
            scoring={responseData.scoring.scoring}
            fileSize={responseData.metadata.file_size_kb}
            dimensions={responseData.metadata.dimensions}
          />
        </div>
      )}
    </div>
  );
};

export default Form;
