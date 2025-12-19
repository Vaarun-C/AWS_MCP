import React from 'react';

interface TerminalHeaderProps {
  status: 'connecting' | 'connected' | 'disconnected';
}

const TerminalHeader: React.FC<TerminalHeaderProps> = ({ status }) => {
  let statusText = 'UNKNOWN';
  let statusColor = 'text-gray-600';
  let dotColor = 'bg-gray-400';

  if (status === 'connected') {
    statusText = 'SYSTEM ONLINE';
    statusColor = 'text-green-700';
    dotColor = 'bg-green-500 animate-pulse';
  } else if (status === 'connecting') {
    statusText = 'ESTABLISHING UPLINK...';
    statusColor = 'text-yellow-600';
    dotColor = 'bg-yellow-500 animate-pulse';
  } else if (status === 'disconnected') {
    statusText = 'CONNECTION LOST';
    statusColor = 'text-red-600';
    dotColor = 'bg-red-600';
  }

  return (
    <div className="mb-4 w-full">
      <div className="border-2 border-black bg-[#f0f0f0] p-2 shadow-[4px_4px_0px_#000000] relative max-w-2xl mx-auto">
        <div className="flex items-center justify-between gap-4 px-2">
          <h1 className="text-lg md:text-xl font-black tracking-widest uppercase">
            Cloud Terminal
          </h1>
          <div className="hidden md:flex gap-4 text-[10px] font-bold font-mono items-center">
            <span>SYS.VER: 1.0.5</span>
            <div className={`flex items-center gap-2 ${statusColor}`}>
              <span className={`block w-2 h-2 rounded-full ${dotColor}`}></span>
              <span>{statusText}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TerminalHeader;
