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