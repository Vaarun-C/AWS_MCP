import React, { useMemo } from 'react';
import { ChatMessage, MessageRole } from '../types';

interface MessageItemProps {
  message: ChatMessage;
  onRunCommand?: (command: string) => void;
}

interface InstanceData {
  id: string;
  status?: string;
  type?: string;
  zone?: string;
  [key: string]: string | undefined;
}

type Segment = 
  | { type: 'text'; content: string }
  | { type: 'instance_group'; items: InstanceData[] };

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

// Advanced parser that turns raw text into structured segments (Text or Instance Groups)
const parseContent = (text: string): Segment[] => {
  const lines = text.split('\n');
  const segments: Segment[] = [];
  
  let currentTextLines: string[] = [];
  let currentInstance: InstanceData | null = null;
  let currentInstanceGroup: InstanceData[] = [];

  const flushText = () => {
    if (currentTextLines.length > 0) {
      // Only push if there's actual content
      const content = currentTextLines.join('\n');
      if (content) {
        segments.push({ type: 'text', content: content });
      }
      currentTextLines = [];
    }
  };

  const flushInstance = () => {
    if (currentInstance) {
      currentInstanceGroup.push(currentInstance);
      currentInstance = null;
    }
  };

  const flushGroup = () => {
    flushInstance();
    if (currentInstanceGroup.length > 0) {
      segments.push({ type: 'instance_group', items: [...currentInstanceGroup] });
      currentInstanceGroup = [];
    }
  };

  // Regex to detect start of an instance block (e.g. "INSTANCE ID: ...")
  const instanceStartRegex = /^(?:INSTANCE[- ]?ID)\s*:\s*(.+)/i;
  // Regex to detect key-value pairs (e.g. "STATUS: RUNNING")
  const keyValueRegex = /^([A-Z0-9\s-]+?)\s*:\s*(.+)/i;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const matchStart = line.match(instanceStartRegex);

    if (matchStart) {
      // We found a new instance header
      flushText();    // Push any preceding text
      flushInstance(); // Finish previous instance if exists (adds to group)
      
      // Start new instance
      currentInstance = { id: matchStart[1].trim() };
      continue;
    }

    if (currentInstance) {
      // We are parsing an instance
      const matchKV = line.match(keyValueRegex);
      if (matchKV) {
        const rawKey = matchKV[1].trim().toUpperCase();
        const value = matchKV[2].trim();
        
        // Normalize keys
        if (rawKey === 'STATUS' || rawKey === 'STATE') currentInstance.status = value;
        else if (rawKey === 'TYPE' || rawKey === 'INSTANCE TYPE') currentInstance.type = value;
        else if (rawKey.includes('ZONE') || rawKey === 'AVAILABILITY-ZONE') currentInstance.zone = value;
        else {
           // clean up key for display
           const cleanKey = rawKey.replace(/\s+/g, '_');
           currentInstance[cleanKey] = value;
        }
      } else if (line.trim() === '') {
        // Empty line might just be spacing within the list
      } else {
        // Line doesn't look like data. 
        // If it's something like "END OF LIST", we finish the group.
        flushGroup(); // Push the group we built
        currentTextLines.push(line); // Treat this line as text
      }
    } else {
      // Just regular text
      currentTextLines.push(line);
    }
  }

  // Final cleanup
  flushText();
  flushGroup();

  return segments;
};

const MessageItem: React.FC<MessageItemProps> = ({ message, onRunCommand }) => {
  const { role, content, isStreaming, timestamp } = message;

  // SYSTEM MESSAGES
  if (role === MessageRole.SYSTEM) {
    return (
      <div className="w-full flex justify-center my-4">
        <div className="text-xs font-bold text-gray-500 bg-gray-100 border border-dashed border-gray-400 px-4 py-1 uppercase tracking-wider">
          &lt; {content} &gt;
        </div>
      </div>
    );
  }

  // LOG MESSAGES
  if (role === MessageRole.LOG) {
    return (
      <div className="w-full flex justify-start mb-2 pr-8 md:pr-20">
         <div className="text-sm text-[#555555] font-mono border border-dashed border-black bg-[#f4f4f4] p-1.5 w-fit">
            <span className="font-bold mr-2">[LOG]</span>
            {content}
         </div>
      </div>
    );
  }

  // USER MESSAGES
  if (role === MessageRole.USER) {
    return (
      <div className="w-full flex justify-end mb-4 pl-8 md:pl-20">
        <div className="w-full max-w-xl border-2 border-[#000080] bg-white shadow-[4px_4px_0px_rgba(0,0,128,0.2)] transform transition-transform hover:-translate-y-0.5">
          <div className="bg-[#000080] text-white px-3 py-1 text-[10px] font-bold flex justify-between items-center border-b-2 border-[#000080]">
            <span>COMMAND_INPUT</span>
            <span className="opacity-75">{formatTime(timestamp)}</span>
          </div>
          {/* Reduced padding (p-3) and font size (text-base) */}
          <div className="p-3 text-right font-mono text-[#000080] bg-[#f8f8ff] font-bold text-base">
            <span className="mr-2 text-gray-400 select-none">&gt;&gt;</span>
            {content}
          </div>
        </div>
      </div>
    );
  }

  // MODEL MESSAGES
  const segments = useMemo(() => parseContent(content), [content]);

  return (
    <div className="w-full flex justify-start mb-4 pr-8 md:pr-20">
      <div className="w-full max-w-4xl border-2 border-black bg-white shadow-[4px_4px_0px_rgba(0,0,0,0.2)]">
        
        {/* Header */}
        <div className="bg-black text-white px-3 py-1 text-[10px] font-bold flex justify-between items-center border-b-2 border-black">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
            <span>ALAIY_CORE_RESPONSE</span>
          </div>
          <span className="opacity-75">{formatTime(timestamp)}</span>
        </div>

        {/* Content Body - Reduced padding (p-4) and font size (text-sm) */}
        <div className="p-4 font-mono text-black leading-relaxed min-h-[40px] text-sm">
          {/* If streaming but no content yet, show loading state */}
          {isStreaming && content.length === 0 && (
             <div className="animate-pulse font-bold text-gray-500">
               PROCESSING...
             </div>
          )}

          {segments.map((segment, index) => {
            if (segment.type === 'text') {
              // Check if this is the last segment to append the cursor
              const isLast = index === segments.length - 1;
              return (
                <div key={index} className="whitespace-pre-wrap mb-4 last:mb-0">
                  {segment.content}
                  {isStreaming && isLast && (
                    <span className="inline-block w-2.5 h-4 bg-black align-middle ml-1 animate-pulse"></span>
                  )}
                </div>
              );
            }

            if (segment.type === 'instance_group') {
              return (
                <div key={index} className="flex flex-wrap gap-4 mb-4 mt-2">
                  {segment.items.map((instance, idx) => (
                    <button 
                      key={idx}
                      onClick={() => onRunCommand && onRunCommand(`tell me about ${instance.id}`)}
                      className="group flex-grow-0 w-full md:w-[calc(50%-0.5rem)] lg:w-[calc(33.33%-0.5rem)] text-left border-2 border-black bg-gray-50 hover:bg-white hover:shadow-[4px_4px_0px_#000080] hover:-translate-y-1 transition-all relative overflow-hidden active:shadow-none active:translate-y-0 active:translate-x-0"
                    >
                      {/* Status indicator strip */}
                      <div className={`absolute top-0 bottom-0 left-0 w-1 ${
                        (instance.status === 'RUNNING') ? 'bg-green-500' : 
                        (instance.status === 'STOPPED') ? 'bg-red-500' : 'bg-yellow-500'
                      }`}></div>

                      <div className="pl-4 pr-3 py-2 border-b border-gray-200 bg-gray-100 flex justify-between items-center">
                        <span className="font-bold text-xs truncate">{instance.id}</span>
                        <div className="bg-black text-white text-[10px] px-1 font-bold">EC2</div>
                      </div>
                      
                      <div className="p-3 pl-4 text-xs space-y-1">
                        {instance.status && (
                          <div className="flex justify-between">
                            <span className="text-gray-500">STATUS:</span>
                            <span className="font-bold">{instance.status}</span>
                          </div>
                        )}
                        {instance.type && (
                          <div className="flex justify-between">
                            <span className="text-gray-500">TYPE:</span>
                            <span>{instance.type}</span>
                          </div>
                        )}
                         {instance.zone && (
                          <div className="flex justify-between">
                            <span className="text-gray-500">ZONE:</span>
                            <span>{instance.zone}</span>
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              );
            }
            return null;
          })}
          
          {/* Fallback cursor if segments logic misses it */}
          {isStreaming && content.length > 0 && segments.length > 0 && segments[segments.length-1].type !== 'text' && (
             <span className="inline-block w-2.5 h-4 bg-black align-middle ml-1 animate-pulse mt-2"></span>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageItem;