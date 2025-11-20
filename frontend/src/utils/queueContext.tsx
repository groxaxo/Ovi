import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';

export interface QueueJob {
  id: string;
  mode: 't2v' | 'i2v';
  prompt: string;
  image: string | null;
  options: {
    seed: number;
    steps: number;
    videoGuidance: number;
    audioGuidance: number;
    resolution: string;
    duration: string;
    solver: string;
    slgLayer: number;
  };
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress?: number;
  videoUrl?: string;
  error?: string;
  createdAt: Date;
}

interface QueueContextType {
  queue: QueueJob[];
  addToQueue: (job: QueueJob) => void;
  removeFromQueue: (id: string) => void;
  clearQueue: () => void;
}

const QueueContext = createContext<QueueContextType | undefined>(undefined);

export const QueueProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [queue, setQueue] = useState<QueueJob[]>([]);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    // Initialize socket connection
    const socketInstance = io('http://localhost:8000', {
      transports: ['websocket'],
      reconnection: true,
    });

    socketInstance.on('connect', () => {
      console.log('Connected to queue server');
    });

    socketInstance.on('job_update', (data: { id: string; status: string; progress?: number; videoUrl?: string; error?: string }) => {
      setQueue(prevQueue =>
        prevQueue.map(job =>
          job.id === data.id
            ? { ...job, status: data.status as any, progress: data.progress, videoUrl: data.videoUrl, error: data.error }
            : job
        )
      );
    });

    socketInstance.on('disconnect', () => {
      console.log('Disconnected from queue server');
    });

    setSocket(socketInstance);

    return () => {
      socketInstance.disconnect();
    };
  }, []);

  const addToQueue = (job: QueueJob) => {
    setQueue(prev => [...prev, job]);
    
    // Send job to backend
    if (socket?.connected) {
      socket.emit('submit_job', job);
    }
  };

  const removeFromQueue = (id: string) => {
    setQueue(prev => prev.filter(job => job.id !== id));
    
    // Notify backend
    if (socket?.connected) {
      socket.emit('cancel_job', { id });
    }
  };

  const clearQueue = () => {
    setQueue([]);
  };

  return (
    <QueueContext.Provider value={{ queue, addToQueue, removeFromQueue, clearQueue }}>
      {children}
    </QueueContext.Provider>
  );
};

export const useQueue = () => {
  const context = useContext(QueueContext);
  if (!context) {
    throw new Error('useQueue must be used within QueueProvider');
  }
  return context;
};
