export interface ChatMessageProps {
  message: string;
  isUser: boolean;
}

export interface ChatInputProps {
  onSend: (message: string) => void;
}

export interface ChatContainerProps {
  messages: { message: string; isUser: boolean }[];
}
export interface Message {
  role: 'assistant' | 'user';
  content: string;
}

export interface ChatHistory {
  "old_message": Message[];
  "input": Message;
}

interface Choices {
  "finish_reason": string;
    "index": number;
    "logprobs": null;
    "message": Message;
}

export interface ChatBotBackendResponse {
  "id": string,
  "choices": Choices[];
  "created": number;
  "model": string;
  "object": string;
  "system_fingerprint": string;
  "usage": {
      "completion_tokens": number;
      "prompt_tokens": number;
      "total_tokens": number;
  }
}