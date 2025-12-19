import React, { FormEvent, useRef, useEffect } from 'react';

interface InputAreaProps {
  input: string;
  isLoading: boolean;
  onInputChange: (val: string) => void;
  onSend: () => void;
}

const InputArea: React.FC<InputAreaProps> = ({ input, isLoading, onInputChange, onSend }) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSend();
  };

  // Auto-focus input on mount and after send
  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  return (
    <div className="pt-6 border-t-2 border-black bg-white sticky bottom-0 pb-6 mt-2 z-10">
      <form onSubmit={handleSubmit} className="flex gap-4 relative">
        <div className="relative flex-grow">
          {/* Decorative label */}
          <div className="absolute -top-3 left-2 bg-white px-1 text-xs font-bold text-gray-500">
             STDIN
          </div>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder={isLoading ? "PROCESSING STREAM..." : "ENTER INSTRUCTION..."}
            disabled={isLoading}
            autoComplete="off"
            className={`
              w-full h-12 px-4 font-mono text-lg bg-white outline-none
              border-2 border-gray-800 focus:border-black
              shadow-[inset_2px_2px_4px_rgba(0,0,0,0.1)]
              placeholder-gray-400 transition-colors
              disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-wait
            `}
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className={`
            h-12 px-8 text-lg font-bold font-mono tracking-wider
            text-white bg-[#000080] outline-none
            border-2 border-black
            shadow-[4px_4px_0px_#000000]
            hover:-translate-y-0.5 hover:shadow-[5px_5px_0px_#000000]
            active:translate-x-[2px] active:translate-y-[2px] active:shadow-none
            disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none disabled:translate-x-0 disabled:translate-y-0
            transition-all duration-75
          `}
        >
          SEND
        </button>
      </form>
    </div>
  );
};

export default InputArea;