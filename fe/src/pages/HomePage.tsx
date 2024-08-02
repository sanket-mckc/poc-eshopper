import React, { useState } from 'react';
import styled from 'styled-components';
import { Container, Typography } from '@mui/material';
import ChatContainer from '../components/ChatContainer';
import ChatInput from '../components/ChatInput';
import { getFollowUpQuestion } from '../services/api';

const HomePage: React.FC = () => {
  const [messages, setMessages] = useState<{ message: string; isUser: boolean }[]>([]);

  const addMessage = (message: string, isUser: boolean) => {
    setMessages((prevMessages) => [...prevMessages, { message, isUser }]);
  };

  const handleSendMessage = async (message: string) => {
    addMessage(message, true);
    // Simulate an API call to get the follow-up question
    const followUpQuestion = await getFollowUpQuestion(message);
    addMessage(followUpQuestion, false);
  };

  return (
    <StyledContainer>
      <Typography variant="h4">GenAI E-Commerce</Typography>
      <ChatContainer messages={messages} />
      <ChatInput onSend={handleSendMessage} />
    </StyledContainer>
  );
};

const StyledContainer = styled(Container)`
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
`;

export default HomePage;
