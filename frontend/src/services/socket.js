import { io } from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000';

let socket = null;

export const initSocket = () => {
  if (!socket) {
    socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });
    
    socket.on('connect', () => {
      console.log('Connected to threat detection server');
    });
    
    socket.on('disconnect', () => {
      console.log('Disconnected from threat detection server');
    });
    
    socket.on('connect_error', (error) => {
      // Silently handle connection errors - backend might not be running
      // Don't log connection refused or transport errors
      const errorMessage = error?.message || '';
      const errorType = error?.type || '';
      const isConnectionError = 
        errorMessage.includes('ECONNREFUSED') ||
        errorMessage.includes('connection') ||
        errorType === 'TransportError' ||
        errorType === 'websocket error';
      
      if (!isConnectionError) {
        console.error('Socket connection error:', error);
      }
    });
  }
  
  return socket;
};

export const getSocket = () => {
  if (!socket) {
    return initSocket();
  }
  return socket;
};

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};


