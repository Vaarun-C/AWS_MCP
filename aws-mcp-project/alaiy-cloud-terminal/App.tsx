import React, { useState, useEffect, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import TerminalHeader from './components/TerminalHeader';
import MessageItem from './components/MessageItem';
import InputArea from './components/InputArea';
import { ChatMessage, MessageRole } from './types';

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';

const App: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const ws = useRef<WebSocket | null>(null);
  const currentAiMsgId = useRef<string | null>(null);
  const reconnectTimeout = useRef<number | null>(null);
  const isUnmounting = useRef(false);

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // WebSocket Connection Logic with Auto-Reconnect
  useEffect(() => {
    isUnmounting.current = false;

    const connect = () => {
      if (isUnmounting.current) return;
      
      setConnectionStatus('connecting');
      const socket = new WebSocket("ws://localhost:8081/ws");
      ws.current = socket;

      socket.onopen = () => {
        console.log("WebSocket Connected");
        setConnectionStatus('connected');
        setMessages(prev => [...prev, {
          id: uuidv4(),
          role: MessageRole.SYSTEM,
          content: 'CONNECTION ESTABLISHED. READY FOR INPUT...',
          timestamp: Date.now()
        }]);
      };

      socket.onclose = () => {
        console.log("WebSocket Disconnected. Retrying in 3s...");
        setConnectionStatus('disconnected');
        ws.current = null;
        
        // Auto-reconnect after 3 seconds
        if (!isUnmounting.current) {
          reconnectTimeout.current = window.setTimeout(() => {
            connect();
          }, 3000);
        }
      };

      socket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        socket.close();
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'log') {
            const logMsg: ChatMessage = {
              id: uuidv4(),
              role: MessageRole.LOG,
              content: data.content,
              timestamp: Date.now()
            };
            setMessages(prev => [...prev, logMsg]);
          } 
          else if (data.type === 'token') {
            if (!currentAiMsgId.current) {
              const newId = uuidv4();
              currentAiMsgId.current = newId;
              
              setMessages(prev => [...prev, {
                id: newId,
                role: MessageRole.MODEL,
                content: data.content,
                timestamp: Date.now(),
                isStreaming: true
              }]);
              setIsWaitingForResponse(true);
            } else {
              setMessages(prev => prev.map(msg => {
                if (msg.id === currentAiMsgId.current) {
                  return { ...msg, content: msg.content + data.content };
                }
                return msg;
              }));
            }
          } 
          else if (data.type === 'end') {
            setMessages(prev => prev.map(msg => {
              if (msg.id === currentAiMsgId.current) {
                return { ...msg, isStreaming: false };
              }
              return msg;
            }));
            currentAiMsgId.current = null;
            setIsWaitingForResponse(false);
          }
        } catch (e) {
          console.error("Error parsing websocket message:", e);
        }
      };
    };

    connect();

    // Cleanup on unmount
    return () => {
      isUnmounting.current = true;
      if (reconnectTimeout.current !== null) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.onclose = null;
        ws.current.close();
      }
    };
  }, []);

  const sendMessage = useCallback((text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    
    // Check if connected - UNCOMMENTED
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.error("WebSocket not ready. State:", ws.current?.readyState);
      alert("System Offline. Please wait for connection...");
      return;
    }

    // Display user message immediately
    setMessages(prev => [...prev, {
      id: uuidv4(),
      role: MessageRole.USER,
      content: trimmed,
      timestamp: Date.now()
    }]);

    setInput('');
    setIsWaitingForResponse(true);

    // Send to backend
    try {
      ws.current.send(JSON.stringify({ message: trimmed }));
    } catch (err) {
      console.error("Failed to send message:", err);
      setIsWaitingForResponse(false);
      alert("Failed to transmit command.");
    }
  }, []);

  const handleInputSend = () => {
    sendMessage(input);
  };

  return (
    <div className="h-full w-full max-w-[1200px] mx-auto flex flex-col bg-paper border-x border-gray-200 shadow-2xl relative">
      <div className="p-4 bg-paper z-10">
        <TerminalHeader status={connectionStatus} />
      </div>

      <div 
        ref={scrollRef} 
        className="flex-1 overflow-y-auto px-4 pb-4"
      >
        {messages.map((msg) => (
          <MessageItem 
            key={msg.id} 
            message={msg} 
            onRunCommand={(cmd) => sendMessage(cmd)}
          />
        ))}
      </div>

      <div className="sticky bottom-0 bg-paper px-4">
        <InputArea
          input={input}
          onInputChange={setInput}
          onSend={handleInputSend}
          isLoading={connectionStatus !== 'connected'}
        />
      </div>
    </div>
  );
};

export default App;