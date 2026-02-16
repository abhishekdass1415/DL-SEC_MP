import React, { useState, useEffect } from 'react';
import { Bell, Clock, Activity, Shield, AlertTriangle } from 'lucide-react';
import { useDashboardStore } from '../../store/dashboardStore';
import { motion } from 'framer-motion';

const Header = () => {
  const { 
    systemStatus, 
    lastUpdate, 
    totalActiveThreats, 
    safeRequests, 
    serverHealth,
    updateLastUpdate 
  } = useDashboardStore();
  
  const [notifications, setNotifications] = useState(0);
  
  useEffect(() => {
    // Update last update time every 5 seconds
    const interval = setInterval(() => {
      updateLastUpdate();
    }, 5000);
    
    return () => clearInterval(interval);
  }, [updateLastUpdate]);
  
  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };
  
  const getStatusColor = () => {
    switch (systemStatus) {
      case 'active': return 'bg-primary-green';
      case 'idle': return 'bg-primary-amber';
      case 'error': return 'bg-primary-red';
      default: return 'bg-gray-500';
    }
  };
  
  const getStatusText = () => {
    switch (systemStatus) {
      case 'active': return 'Active';
      case 'idle': return 'Idle';
      case 'error': return 'Error';
      default: return 'Unknown';
    }
  };
  
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-dark-surface border-b border-dark-border">
      {/* Summary Strip */}
      <div className="bg-gradient-to-r from-dark-card to-dark-surface px-6 py-2 border-b border-dark-border">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-primary-cyan" />
              <span className="text-gray-400">Active Threats:</span>
              <span className="font-semibold text-white">{totalActiveThreats}</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary-green" />
              <span className="text-gray-400">Safe Requests:</span>
              <span className="font-semibold text-white">{safeRequests.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
              <span className="text-gray-400">Server Health:</span>
              <span className="font-semibold text-white">{serverHealth}%</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <Clock className="w-4 h-4" />
            <span>Last Updated: {formatTime(lastUpdate)}</span>
          </div>
        </div>
      </div>
      
      {/* Main Header */}
      <div className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-cyan to-primary-blue rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">DL-SEC</h1>
              <p className="text-xs text-gray-400">Threat Detection System</p>
            </div>
          </div>
          
          {/* System Status Indicator */}
          <div className="flex items-center gap-2 ml-4 pl-4 border-l border-dark-border">
            <motion.div
              className={`w-3 h-3 rounded-full ${getStatusColor()}`}
              animate={{ 
                scale: systemStatus === 'active' ? [1, 1.2, 1] : 1,
                opacity: systemStatus === 'active' ? [1, 0.7, 1] : 1
              }}
              transition={{ 
                duration: 2, 
                repeat: systemStatus === 'active' ? Infinity : 0 
              }}
            />
            <span className="text-sm font-medium text-white">{getStatusText()}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <div className="relative">
            <button className="relative p-2 rounded-lg hover:bg-dark-hover transition-colors">
              <Bell className="w-5 h-5 text-gray-400" />
              {notifications > 0 && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-primary-red rounded-full flex items-center justify-center"
                >
                  <span className="text-xs font-bold text-white">{notifications}</span>
                </motion.div>
              )}
            </button>
          </div>
          
          {/* Settings */}
          <button className="p-2 rounded-lg hover:bg-dark-hover transition-colors">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
