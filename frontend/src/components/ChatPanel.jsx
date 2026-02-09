// src/components/ChatPanel.jsx
// AI Chat Interface

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

const ChatPanel = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your HIVE AD AGENT assistant. Ask me anything about campaigns, users, or analytics!',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const aiMessage = {
        role: 'assistant',
        content: `I received your message: "${input}". This is a simulated response. Connect to the backend API for real AI responses!`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      setLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-yellow-400/20 flex flex-col h-[600px]">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <h2 className="text-xl font-bold text-white flex items-center space-x-2">
          <Bot className="w-6 h-6 text-yellow-400" />
          <span>AI Assistant</span>
        </h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] p-3 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-yellow-500 text-slate-900'
                  : 'bg-slate-700 text-white'
              }`}
            >
              <div className="flex items-center space-x-2 mb-1">
                {msg.role === 'user' ? (
                  <User className="w-4 h-4" />
                ) : (
                  <Bot className="w-4 h-4" />
                )}
                <span className="text-xs font-semibold">
                  {msg.role === 'user' ? 'You' : 'AI'}
                </span>
              </div>
              <p className="text-sm">{msg.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 text-white p-3 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-pulse">🤔</div>
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="bg-yellow-400 text-slate-900 px-4 py-2 rounded-lg hover:bg-yellow-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;