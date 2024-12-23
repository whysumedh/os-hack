import React from 'react';
import PropTypes from 'prop-types';
import './ColorPalette.css'; // Optional for additional styling

const ColorPalette = ({ brand_palette }) => {
    return (
        <div className="color-palette">
            {brand_palette.map((color, index) => (
                <div
                    key={index}
                    className="color-swatch"
                    style={{ backgroundColor: color }}
                    title={color} // Tooltip to show the color code
                >
                    <span className="color-label">{color}</span>
                </div>
            ))}
        </div>
    );
};

ColorPalette.propTypes = {
    brand_palette: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default ColorPalette;