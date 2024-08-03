import React, { useState, ChangeEvent } from 'react';
import { useChat } from '../context/ChatContext';
import { Message } from '../types';
import { getFollowUpQuestion } from '../services/api';

const Chatbot: React.FC = () => {
  const { messages, addMessage } = useChat();
  const [input, setInput] = useState<string>('');

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const sendChatToTheBackend = async (newMessage: Message) => {
    const backendResponse = await getFollowUpQuestion({
      "old_message": messages,
      "input": newMessage,
    });
    addMessage(backendResponse.choices[0].message);
  };

  const handleSendMessage = () => {
    if (input.trim() === '') return;

    const newMessage: Message = {
      role: 'user',
      content: input,
    };

    addMessage(newMessage);
    sendChatToTheBackend(newMessage);
    setInput('');
  };


  return (
    <div className="flex flex-col items-center">
      <div className="flex flex-col w-full p-4 bg-white shadow-lg rounded-lg mt-10">
        <div className="flex flex-col flex-grow overflow-y-auto h-80 border-b-2 mb-4">
          {messages.map((message) => (
            <div
              key={message.content}
              className={`p-2 my-2 rounded-md ${message.role === 'assistant' ? 'bg-blue-100 self-start' : 'bg-green-100 self-end'
                }`}
            >
              {message.content}
            </div>
          ))}
        </div>
        <div className="flex">
          <input
            type="text"
            className="flex-grow p-2 border rounded-l-md focus:outline-none"
            value={input}
            onChange={handleInputChange}
            placeholder="Type a message..."
          />
          <button
            className="p-2 bg-blue-500 text-white rounded-r-md"
            onClick={handleSendMessage}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
