'use client';

import { useState, useRef, useEffect } from 'react';
import { FiSend, FiMessageSquare, FiUser, FiCpu, FiAlertCircle } from 'react-icons/fi';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: string[];
  confidence?: string;
}

interface ChatInterfaceProps {
  companySymbol?: string;
}

export default function ChatInterface({ companySymbol }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello! I am your financial AI assistant. Ask me anything about company financials, risk assessments, or forensic analysis.',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/qa/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.content,
          company_symbol: companySymbol,
          max_context: 5
        }),
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.answer,
          timestamp: data.timestamp || new Date().toISOString(),
          sources: data.sources,
          confidence: data.confidence
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again later.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="neumorphic-card rounded-2xl overflow-hidden flex flex-col h-[600px]" style={{ background: '#f0f0f0', boxShadow: '12px 12px 24px #d0d0d0, -12px -12px 24px #ffffff' }}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between" style={{ background: '#f0f0f0' }}>
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center neumorphic-inset" style={{ background: '#f0f0f0', boxShadow: 'inset 4px 4px 8px #d0d0d0, inset -4px -4px 8px #ffffff' }}>
            <FiCpu className="w-5 h-5 text-indigo-500" />
          </div>
          <div>
            <h3 className="font-bold text-gray-800">IRIS Assistant</h3>
            <p className="text-xs text-gray-500">{companySymbol ? `Analyzing ${companySymbol}` : 'Financial Expert'}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          <span className="text-xs text-gray-500">Online</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl p-4 ${
                msg.role === 'user'
                  ? 'bg-indigo-500 text-white rounded-tr-none shadow-lg'
                  : 'bg-white text-gray-800 rounded-tl-none shadow-md'
              }`}
              style={msg.role === 'assistant' ? { boxShadow: '4px 4px 8px #d0d0d0, -4px -4px 8px #ffffff' } : {}}
            >
              <div className="flex items-center space-x-2 mb-1 opacity-70 text-xs">
                {msg.role === 'user' ? <FiUser /> : <FiCpu />}
                <span>{msg.role === 'user' ? 'You' : 'IRIS AI'}</span>
              </div>
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {msg.content}
              </div>
              
              {/* Metadata for assistant messages */}
              {msg.role === 'assistant' && (msg.sources || msg.confidence) && (
                <div className="mt-3 pt-3 border-t border-gray-100 text-xs flex flex-wrap gap-2 text-gray-500">
                  {msg.confidence && (
                    <span className={`px-2 py-1 rounded-full ${
                      msg.confidence === 'High' ? 'bg-green-100 text-green-700' :
                      msg.confidence === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      Confidence: {msg.confidence}
                    </span>
                  )}
                  {msg.sources && msg.sources.length > 0 && (
                    <span className="px-2 py-1 rounded-full bg-blue-50 text-blue-600">
                      Sources: {msg.sources.length}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl rounded-tl-none p-4 shadow-md flex items-center space-x-2">
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex items-center space-x-2 bg-gray-100 rounded-xl p-2 neumorphic-inset" style={{ boxShadow: 'inset 4px 4px 8px #d0d0d0, inset -4px -4px 8px #ffffff' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask about financial data..."
            className="flex-1 bg-transparent border-none focus:ring-0 text-gray-700 placeholder-gray-400 px-2"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`p-2 rounded-lg transition-all ${
              !input.trim() || isLoading
                ? 'text-gray-400 cursor-not-allowed'
                : 'bg-indigo-500 text-white shadow-lg hover:bg-indigo-600'
            }`}
          >
            <FiSend className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
