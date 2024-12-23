import React, { useEffect, useState } from "react";

const ButtonColorPicker = ({ color, onColorChange }) => {
  const [localColor, setLocalColor] = useState(color || "#000000");

  useEffect(() => {
    // Sync with the parent color prop when it changes
    setLocalColor(color);
  }, [color]);

  const handleChange = (event) => {
    const newColor = event.target.value;
    setLocalColor(newColor);
    onColorChange(newColor);
  };

  return (
    <div style={{ textAlign: "center" }}>
      {/* Color Picker */}
      <input
        type="color"
        value={localColor}
        onChange={handleChange}
        style={{
          border: "none",
          background: "none",
          cursor: "pointer",
          width: "50px",
          height: "50px",
          marginBottom: "5px",
        }}
      />
      {/* Display HEX Code */}
      <input
        type="text"
        value={localColor}
        readOnly
        style={{
          textAlign: "center",
          width: "90px",
          border: "1px solid #ccc",
          padding: "5px",
          borderRadius: "5px",
          fontSize: "12px",
        }}
      />
    </div>
  );
};

export default ButtonColorPicker;
