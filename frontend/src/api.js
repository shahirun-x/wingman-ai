import axios from 'axios';

// This points to your FastAPI backend
const API_URL = "https://friendly-lamp-4j9wjjp7vgxxhqj66-8000.app.github.dev";

export const sendMessage = async (message) => {
  try {
    const response = await axios.post(`${API_URL}/chat`, {
      user_message: message,
      mood: "neutral" // We will make this dynamic later
    });
    return response.data;
  } catch (error) {
    console.error("Error talking to Wingman:", error);
    return null;
  }
};