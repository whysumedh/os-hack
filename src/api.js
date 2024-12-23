import axios from 'axios';

const API_BASE_URL = "https://creative-api-141459457956.us-central1.run.app/generate_creative"; // Replace with your API's base URL

export const fetchCreativeScoring = async (inputPayload) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/score-creative`, inputPayload);
        return response.data;
    } catch (error) {
        console.error("Error fetching scoring data:", error);
        throw error;
    }
};
