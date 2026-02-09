// src/components/WorkflowPanel.jsx
// Workflow Execution Panel

import React, { useState } from 'react';
import { Play, Loader } from 'lucide-react';
import { executeWorkflow } from '../services/api';

const WorkflowPanel = ({ onWorkflowComplete }) => {
  const [userId, setUserId] = useState('demo_user_001');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleExecute = async () => {
    setLoading(true);
    setResult(null);

    try {
      const workflowResult = await executeWorkflow('full_ad_campaign', {
        user_id: userId,
        products: [
          {
            id: 'prod_001',
            title: 'Smart Watch Pro',
            price: 299.99,
            category: 'Electronics'
          },
          {
            id: 'prod_002',
            title: 'Wireless Earbuds',
            price: 149.99,
            category: 'Electronics'
          }
        ]
      });

      setResult(workflowResult);
      
      if (onWorkflowComplete) {
        onWorkflowComplete(workflowResult);
      }
    } catch (error) {
      setResult({
        success: false,
        error: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-yellow-400/20">
      <h2 className="text-xl font-bold text-white mb-4">🎯 Execute Workflow</h2>

      <div className="space-y-4">
        {/* User ID Input */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            User ID
          </label>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
            placeholder="Enter user ID"
          />
        </div>

        {/* Execute Button */}
        <button
          onClick={handleExecute}
          disabled={loading}
          className="w-full bg-gradient-to-r from-yellow-400 to-orange-500 text-slate-900 font-bold py-3 px-6 rounded-lg hover:from-yellow-500 hover:to-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              <span>Executing...</span>
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              <span>Execute Full Campaign</span>
            </>
          )}
        </button>

        {/* Result Display */}
        {result && (
          <div className={`mt-4 p-4 rounded-lg ${result.success ? 'bg-green-500/20 border border-green-500/50' : 'bg-red-500/20 border border-red-500/50'}`}>
            <h3 className="font-bold text-white mb-2">
              {result.success ? '✅ Workflow Complete!' : '❌ Workflow Failed'}
            </h3>
            
            {result.success ? (
              <div className="text-sm text-gray-300 space-y-1">
                <p>Workflow ID: {result.workflow_id}</p>
                <p>Execution Time: {result.execution_time?.toFixed(2)}s</p>
                <p>Bees Involved: {result.bees_involved?.join(', ')}</p>
              </div>
            ) : (
              <p className="text-sm text-red-300">{result.error}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowPanel;