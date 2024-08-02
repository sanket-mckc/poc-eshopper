import React from 'react';
import styled from 'styled-components';
import { Typography } from '@mui/material';
import { ChatMessageProps } from '../types';

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser }) => {
  return (
    <MessageContainer isUser={isUser}>
      <Typography variant="body1">{message}</Typography>
    </MessageContainer>
  );
};

const MessageContainer = styled.div<{ isUser: boolean }>`
  background-color: ${({ isUser }) => (isUser ? '#DCF8C6' : '#FFF')};
  border-radius: 10px;
  padding: 10px;
  margin: 5px 0;
  align-self: ${({ isUser }) => (isUser ? 'flex-end' : 'flex-start')};
  max-width: 70%;
`;

export default ChatMessage;
