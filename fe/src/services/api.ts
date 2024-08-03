import axios from 'axios';
import { ChatHistory, ChatBotBackendResponse } from '../types';

const API_URL = 'http://localhost:5002'; // Replace with your API URL

export const getFollowUpQuestion = async (chatHistory: ChatHistory): Promise<ChatBotBackendResponse> => {
  const response = await axios.post(`${API_URL}/sales-assistant`, chatHistory);
  return response.data;
};

export const getMoodBoardImages = async (responses: any): Promise<any> => {
  const response = await axios.post(`${API_URL}/mood-board`, { responses });
  return response.data;
};
