// src/components/Dashboard.jsx
// Main Dashboard Component

import React, { useState, useEffect } from 'react';
import { Activity, DollarSign, Zap, TrendingUp } from 'lucide-react';
import AgentCard from './AgentCard';
import MetricsCard from './MetricsCard';
import WorkflowPanel from './WorkflowPanel';
import ChatPanel from './ChatPanel';
import { getSystemStatus, getAIUsageStats } from '../services/api';

const Dashboard = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [aiUsage, setAiUsage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    
    // Refresh every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [status, usage] = await Promise.all([
        getSystemStatus(),
        getAIUsageStats()
      ]);
      
      setSystemStatus(status);
      setAiUsage(usage);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-yellow-400 mb-4"></div>
          <h2 className="text-2xl font-bold text-white">Loading HIVE AD AGENT...</h2>
        </div>
      </div>
    );
  }

  // Mock agents data (replace with actual data from systemStatus)
  const agents = [
    {
      id: 'queen_bee_001',
      name: 'Queen Bee',
      role: 'Orchestrator',
      state: 'idle',
      icon: '👑',
      tasks_completed: systemStatus?.workflows_completed || 0,
      messages_sent: 12
    },
    {
      id: 'shopper_bee_001',
      name: 'Shopper Bee',
      role: 'Shopping Analyst',
      state: 'thinking',
      icon: '🛍️',
      tasks_completed: 5,
      messages_sent: 8,
      current_task: 'Analyzing user behavior...'
    },
    {
      id: 'ad_bee_001',
      name: 'Ad Bee',
      role: 'Campaign Creator',
      state: 'working',
      icon: '📢',
      tasks_completed: 3,
      messages_sent: 6,
      current_task: 'Creating ad campaign...'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-lg border-b border-yellow-400/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-4xl">🐝</div>
              <div>
                <h1 className="text-2xl font-bold text-white">HIVE AD AGENT</h1>
                <p className="text-sm text-gray-400">Collective Intelligence for Intelligent Advertising</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-4 py-2 bg-green-500/20 rounded-lg border border-green-500/50">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-400 font-semibold">System Online</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricsCard
            icon={Activity}
            title="Active Agents"
            value={agents.length}
            subtitle="All systems operational"
            color="blue"
          />
          <MetricsCard
            icon={Zap}
            title="Workflows"
            value={systemStatus?.workflows_completed || 0}
            subtitle="Completed today"
            color="green"
          />
          <MetricsCard
            icon={TrendingUp}
            title="AI Requests"
            value={aiUsage?.total_requests || 0}
            subtitle={`${aiUsage?.total_tokens?.toLocaleString() || 0} tokens`}
            color="purple"
          />
          <MetricsCard
            icon={DollarSign}
            title="AI Cost"
            value={`$${(aiUsage?.total_cost || 0).toFixed(4)}`}
            subtitle="This session"
            color="yellow"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Agents */}
          <div className="lg:col-span-2 space-y-6">
            {/* Agents Grid */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center space-x-2">
                <span>🐝</span>
                <span>Active Agents</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {agents.map((agent) => (
                  <AgentCard key={agent.id} agent={agent} />
                ))}
              </div>
            </div>

            {/* Workflow Panel */}
            <WorkflowPanel onWorkflowComplete={fetchData} />
          </div>

          {/* Right Column - Chat */}
          <div>
            <ChatPanel />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;