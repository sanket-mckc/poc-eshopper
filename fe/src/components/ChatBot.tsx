import React, { useState, ChangeEvent } from 'react';

interface Message {
  role: 'bot' | 'user';
  text: string;
}

const Chatbot: React.FC = () => {
  const botFirstMessage: Message = {
    role: 'bot',
    text: 'What would you like to shop for today?',
  };
  const [messages, setMessages] = useState<Message[]>([botFirstMessage]);
  const [input, setInput] = useState<string>('');

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleSendMessage = () => {
    if (input.trim() === '') return;

    const newMessage: Message = {
      role: 'user',
      text: input,
    };

    setMessages([...messages, newMessage]);
    setInput('');
  };


  return (
    <div className="flex flex-col items-center">
      <div className="flex flex-col w-full p-4 bg-white shadow-lg rounded-lg mt-10">
        <div className="flex flex-col flex-grow overflow-y-auto h-80 border-b-2 mb-4">
          {messages.map((message) => (
            <div
              key={message.text}
              className={`p-2 my-2 rounded-md ${
                message.role === 'bot' ? 'bg-blue-100 self-start' : 'bg-green-100 self-end'
              }`}
            >
              {message.text}
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
