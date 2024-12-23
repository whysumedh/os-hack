export const mockApiRequest = async (inputPayload) => {
    console.log("Received Payload:", inputPayload);

    // Simulated API response
    const mockResponse = {
        status: "success",
        creative_url: "https://example.com/generated_creative.png",
        scoring: {
            background_foreground_separation: 18,
            brand_guideline_adherence: 19,
            creativity_visual_appeal: 16,
            product_focus: 15,
            call_to_action: 14,
            audience_relevance: 9,
            total_score: 91,
        },
        metadata: {
            file_size_kb: 320,
            dimensions: { width: 1080, height: 1080 },
        },
    };

    // Simulate a delay like a real API
    return new Promise((resolve) => setTimeout(() => resolve(mockResponse), 1000));
};
