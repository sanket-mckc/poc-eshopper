import React from 'react';
import styled from 'styled-components';
import ChatMessage from './ChatMessage';
import { ChatContainerProps } from '../types';

const ChatContainer: React.FC<ChatContainerProps> = ({ messages }) => {
  return (
    <MessagesContainer>
      {messages.map((msg) => (
        <ChatMessage key={msg.message[0]} message={msg.message} isUser={msg.isUser} />
      ))}
    </MessagesContainer>
  );
};

const MessagesContainer = styled.div`
  display: flex;
  flex-direction: column;
  padding: 10px;
  padding-bottom: 70px; // To ensure messages are not hidden behind the input
  overflow-y: auto;
  height: calc(100vh - 70px); // Adjust height to leave space for the input
`;

export default ChatContainer;
