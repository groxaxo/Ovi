import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, CheckCircle, XCircle, Loader, Trash2, Download } from 'lucide-react';
import { useQueue } from '@/utils/queueContext';

const QueuePanel: React.FC = () => {
  const { queue, removeFromQueue } = useQueue();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'queued':
        return <Clock className="w-5 h-5 text-yellow-400" />;
      case 'processing':
        return <Loader className="w-5 h-5 text-primary-400 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued':
        return 'bg-yellow-500/10 border-yellow-500/50';
      case 'processing':
        return 'bg-primary-500/10 border-primary-500/50';
      case 'completed':
        return 'bg-green-500/10 border-green-500/50';
      case 'failed':
        return 'bg-red-500/10 border-red-500/50';
      default:
        return 'bg-gray-500/10 border-gray-500/50';
    }
  };

  return (
    <div className="card h-full">
      <div className="card-header flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Generation Queue</h2>
        <span className="text-sm text-gray-400">
          {queue.filter(j => j.status === 'queued' || j.status === 'processing').length} active
        </span>
      </div>

      <div className="p-4 space-y-3 max-h-[calc(100vh-12rem)] overflow-y-auto">
        <AnimatePresence>
          {queue.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <Clock className="w-12 h-12 mx-auto text-gray-600 mb-3" />
              <p className="text-gray-400">No jobs in queue</p>
              <p className="text-sm text-gray-500 mt-1">
                Create a video to get started
              </p>
            </motion.div>
          ) : (
            queue.map((job) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className={`p-4 rounded-lg border ${getStatusColor(job.status)} transition-all`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(job.status)}
                    <span className="text-sm font-medium text-white capitalize">
                      {job.status}
                    </span>
                  </div>
                  <button
                    onClick={() => removeFromQueue(job.id)}
                    className="text-gray-400 hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <p className="text-sm text-gray-300 line-clamp-2 mb-2">
                  {job.prompt}
                </p>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{job.mode.toUpperCase()}</span>
                  <span>{job.options.resolution}</span>
                </div>

                {/* Progress Bar */}
                {job.status === 'processing' && job.progress !== undefined && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                      <span>Progress</span>
                      <span>{job.progress}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${job.progress}%` }}
                        className="h-full bg-primary-500"
                      />
                    </div>
                  </div>
                )}

                {/* Completed Video */}
                {job.status === 'completed' && job.videoUrl && (
                  <div className="mt-3">
                    <video
                      src={job.videoUrl}
                      controls
                      className="w-full rounded-lg"
                    />
                    <button className="btn-secondary w-full mt-2 text-sm py-2">
                      <Download className="w-4 h-4 inline-block mr-2" />
                      Download
                    </button>
                  </div>
                )}

                {/* Error Message */}
                {job.status === 'failed' && job.error && (
                  <div className="mt-2 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
                    {job.error}
                  </div>
                )}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default QueuePanel;
