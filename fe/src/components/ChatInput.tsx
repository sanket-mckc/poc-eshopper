import React, { useState } from 'react';
import { TextField, Button } from '@mui/material';
import styled from 'styled-components';
import { ChatInputProps } from '../types';


const ChatInput: React.FC<ChatInputProps> = ({ onSend }) => {
  const [input, setInput] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleSend = () => {
    onSend(input);
    setInput('');
  };

  return (
    <InputContainer>
      <TextField
        label="Type a message..."
        value={input}
        onChange={handleChange}
        fullWidth
        variant="outlined"
      />
      <Button onClick={handleSend} variant="contained" color="primary">
        Send
      </Button>
    </InputContainer>
  );
};

const InputContainer = styled.div`
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #f5f5f5;
  position: fixed;
  bottom: 0;
  width: 100%;
`;

export default ChatInput;
