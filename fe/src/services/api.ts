import axios from 'axios';

const API_URL = 'https://api.example.com'; // Replace with your API URL

export const getFollowUpQuestion = async (input: string): Promise<string> => {
  const response = await axios.post(`${API_URL}/follow-up`, { input });
  return response.data.question;
};

export const getMoodBoardImages = async (responses: any): Promise<any> => {
  const response = await axios.post(`${API_URL}/mood-board`, { responses });
  return response.data;
};
