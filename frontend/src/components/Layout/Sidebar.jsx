import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Monitor, Briefcase, FileText, Settings, Database, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';

const Sidebar = () => {
  const [hoveredItem, setHoveredItem] = useState(null);

  const menuItems = [
    { icon: Home, label: 'Home', to: '/dashboard', description: 'Main dashboard' },
    { icon: Monitor, label: 'Real-Time Monitor', to: '/monitor', badge: true, description: 'Live monitoring' },
    { icon: Briefcase, label: 'Threat Analytics', to: '/analytics', description: 'Threat analysis' },
    { icon: BarChart3, label: 'Model Insights', to: '/insights', description: 'Model performance' },
    { icon: Database, label: 'Dataset', to: '/dataset', description: 'Dataset management' },
    { icon: FileText, label: 'Logs', to: '/logs', description: 'System logs' },
    { icon: Settings, label: 'Settings', to: '/settings', description: 'System settings' },
  ];

  return (
    <aside className="fixed left-0 top-32 bottom-0 w-60 bg-dark-surface border-r border-dark-border z-40 overflow-y-auto">
      <nav className="p-4 space-y-2">
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              onMouseEnter={() => setHoveredItem(index)}
              onMouseLeave={() => setHoveredItem(null)}
              className="relative"
            >
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-blue/20 text-primary-cyan border border-primary-blue/50'
                      : 'text-gray-400 hover:bg-dark-hover hover:text-white'
                  }`
                }
              >
                <Icon size={20} />
                <span className="font-medium">{item.label}</span>
                {item.badge && (
                  <span className="ml-auto w-2 h-2 bg-primary-red rounded-full animate-pulse" />
                )}
              </NavLink>
              
              {/* Tooltip */}
              {hoveredItem === index && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="absolute left-full ml-2 top-1/2 -translate-y-1/2 z-50 px-3 py-2 bg-dark-card border border-dark-border rounded-lg shadow-xl whitespace-nowrap"
                >
                  <div className="text-sm text-white">{item.description}</div>
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-full w-0 h-0 border-t-4 border-t-transparent border-r-4 border-r-dark-border border-b-4 border-b-transparent" />
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;
