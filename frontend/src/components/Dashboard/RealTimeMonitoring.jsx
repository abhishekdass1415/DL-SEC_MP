import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';
import { useThreats } from '../../context/ThreatContext';

const RealTimeMonitoring = () => {
  const { threats } = useThreats();

  const recent = useMemo(() => {
    if (!threats || threats.length === 0) return [];
    const sorted = [...threats].sort(
      (a, b) => new Date(b.timestamp) - new Date(a.timestamp),
    );
    return sorted.slice(0, 4);
  }, [threats]);

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-300 mb-3">Live Network Activity Feed</h4>
      {recent.length > 0 ? (
        recent.map((item, index) => {
          const activityLevel = Math.min(90, Math.max(20, Math.round((item.confidence || 0.6) * 100)));
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="space-y-1"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-300 font-medium">{item.source_ip || 'Unknown'}</span>
                <span className="text-gray-500">{activityLevel}%</span>
              </div>
              <div className="w-full bg-dark-border rounded-full h-2 overflow-hidden">
                <motion.div
                  className="bg-gradient-to-r from-primary-cyan to-primary-blue h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${activityLevel}%` }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                />
              </div>
            </motion.div>
          );
        })
      ) : (
        <div className="text-center py-8 text-gray-400 text-sm">
          <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>No recent activity</p>
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-dark-border">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">Traffic Volume</h4>
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Normal</span>
            <span>Suspicious</span>
          </div>
          <div className="w-full bg-dark-border rounded-full h-3 overflow-hidden">
            <motion.div
              className="bg-gradient-to-r from-primary-green via-primary-amber to-primary-red h-3 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(95, recent.length * 15)}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeMonitoring;
