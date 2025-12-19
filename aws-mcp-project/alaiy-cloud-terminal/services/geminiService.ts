import { GoogleGenAI, Chat, GenerateContentResponse } from "@google/genai";
import { ChatMessage, MessageRole } from "../types";

// Initialize the API client
// Ideally, in a production app, you would proxy this through a backend to hide the key,
// or require the user to input their own key for a static site.
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const SYSTEM_INSTRUCTION = `You are the Alaiy Cloud Terminal (V1.0). 
You exist within a retro-futuristic, text-only terminal environment.
Your responses should be concise, technical, slightly robotic but helpful.
Do not use markdown bolding or italics excessively. 
Use uppercase for emphasis if needed.
Maintain the persona of a high-end cloud mainframe from the 90s.`;

let chatSession: Chat | null = null;

export const initializeChat = () => {
  chatSession = ai.chats.create({
    model: 'gemini-2.5-flash',
    config: {
      systemInstruction: SYSTEM_INSTRUCTION,
      temperature: 0.7,
    },
    history: []
  });
};

export const sendMessageStream = async (
  message: string, 
  onChunk: (text: string) => void
): Promise<void> => {
  if (!chatSession) {
    initializeChat();
  }

  if (!chatSession) throw new Error("Failed to initialize chat session");

  try {
    const result = await chatSession.sendMessageStream({ message });
    
    for await (const chunk of result) {
      const responseChunk = chunk as GenerateContentResponse;
      if (responseChunk.text) {
        onChunk(responseChunk.text);
      }
    }
  } catch (error) {
    console.error("Gemini API Error:", error);
    onChunk("\n[SYSTEM ERROR]: CONNECTION INTERRUPTED. PLEASE RETRY.");
  }
};