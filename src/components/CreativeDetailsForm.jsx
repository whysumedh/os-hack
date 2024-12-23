import React from "react";
import ButtonColorPicker from "./ColorBox";

const CreativeDetailsForm = ({ formData, handleInputChange, handleArrayChange }) => {
  const handleColorChange = (index, color) => {
    handleArrayChange(index, color);
  };

  return (
    <div className="form-section">
      <h2>Creative Details</h2>
      
      {/* Product Name */}
      <label>
        Product Name:
        <input
          type="text"
          name="product_name"
          value={formData.product_name}
          onChange={handleInputChange}
        />
      </label>

      {/* Tagline */}
      <label>
        Tagline:
        <input
          type="text"
          name="tagline"
          value={formData.tagline}
          onChange={handleInputChange}
        />
      </label>

      {/* Brand Palette with Three Color Pickers */}
      <label>
        Brand Palette:
        <div className="brand-palette" style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
          {formData.brand_palette.map((color, index) => (
            <ButtonColorPicker
              key={index}
              color={color}
              onColorChange={(newColor) => handleColorChange(index, newColor)}
            />
          ))}
        </div>
      </label>

      {/* Dimensions */}
      <label>
        Dimensions (Width):
        <input
          type="number"
          name="width"
          value={formData.width}
          onChange={handleInputChange}
        />
      </label>
      <label>
        Dimensions (Height):
        <input
          type="number"
          name="height"
          value={formData.height}
          onChange={handleInputChange}
        />
      </label>

      {/* CTA Text */}
      <label>
        CTA Text:
        <input
          type="text"
          name="cta_text"
          value={formData.cta_text}
          onChange={handleInputChange}
        />
      </label>

      {/* Logo URL */}
      <label>
        Logo URL:
        <input
          type="text"
          name="logo_url"
          value={formData.logo_url}
          onChange={handleInputChange}
        />
      </label>

      {/* Product Image URL */}
      <label>
        Product Image URL:
        <input
          type="text"
          name="product_image_url"
          value={formData.product_image_url}
          onChange={handleInputChange}
        />
      </label>
    </div>
  );
};

export default CreativeDetailsForm;
