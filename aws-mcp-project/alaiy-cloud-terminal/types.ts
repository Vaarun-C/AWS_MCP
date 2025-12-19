export enum MessageRole {
  SYSTEM = 'system',
  USER = 'user',
  MODEL = 'model',
  LOG = 'log'
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
  isStreaming?: boolean;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  inputText: string;
}