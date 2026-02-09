// src/components/AgentCard.jsx
// Individual Agent Status Card

import React from 'react';
import { Activity, Brain, Zap, CheckCircle } from 'lucide-react';

const AgentCard = ({ agent }) => {
  const getStateIcon = (state) => {
    switch (state) {
      case 'thinking':
        return <Brain className="w-5 h-5 text-purple-400 animate-pulse" />;
      case 'working':
        return <Zap className="w-5 h-5 text-yellow-400 animate-bounce" />;
      case 'idle':
        return <Activity className="w-5 h-5 text-green-400" />;
      default:
        return <CheckCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStateColor = (state) => {
    switch (state) {
      case 'thinking':
        return 'bg-purple-500/20 border-purple-500/50';
      case 'working':
        return 'bg-yellow-500/20 border-yellow-500/50';
      case 'idle':
        return 'bg-green-500/20 border-green-500/50';
      default:
        return 'bg-gray-500/20 border-gray-500/50';
    }
  };

  return (
    <div className={`p-6 rounded-xl border-2 ${getStateColor(agent.state)} backdrop-blur-lg transition-all hover:scale-105`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="text-3xl">{agent.icon || '🐝'}</div>
          <div>
            <h3 className="text-lg font-bold text-white">{agent.name}</h3>
            <p className="text-sm text-gray-400">{agent.role}</p>
          </div>
        </div>
        {getStateIcon(agent.state)}
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">State:</span>
          <span className="text-white font-semibold capitalize">{agent.state}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Tasks:</span>
          <span className="text-white font-semibold">{agent.tasks_completed || 0}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Messages:</span>
          <span className="text-white font-semibold">{agent.messages_sent || 0}</span>
        </div>
      </div>

      {agent.current_task && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <p className="text-xs text-gray-400">Current Task:</p>
          <p className="text-sm text-white mt-1">{agent.current_task}</p>
        </div>
      )}
    </div>
  );
};

export default AgentCard;