import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Wand2, Settings, Image as ImageIcon, FileText } from 'lucide-react';
import { useQueue } from '@/utils/queueContext';
import PromptTemplates from './PromptTemplates';

const VideoGenerator: React.FC = () => {
  const { addToQueue } = useQueue();
  const [mode, setMode] = useState<'t2v' | 'i2v'>('t2v');
  const [prompt, setPrompt] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);

  // Advanced options
  const [options, setOptions] = useState({
    seed: 100,
    steps: 50,
    videoGuidance: 4.0,
    audioGuidance: 3.0,
    resolution: '960x960',
    duration: '10s',
    solver: 'unipc',
    slgLayer: 11,
  });

  const handleGenerate = () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    if (mode === 'i2v' && !image) {
      alert('Please upload an image for Image-to-Video mode');
      return;
    }

    const job = {
      id: Date.now().toString(),
      mode,
      prompt,
      image: image ? URL.createObjectURL(image) : null,
      options,
      status: 'queued' as const,
      createdAt: new Date(),
    };

    addToQueue(job);
    
    // Clear form
    setPrompt('');
    setImage(null);
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0]);
    }
  };

  const applyTemplate = (template: string) => {
    setPrompt(template);
    setShowTemplates(false);
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Wand2 className="w-6 h-6 mr-2 text-primary-400" />
          Generate Video
        </h2>
      </div>

      <div className="card-body space-y-6">
        {/* Mode Selection */}
        <div>
          <label className="label">Generation Mode</label>
          <div className="flex space-x-4">
            <button
              onClick={() => setMode('t2v')}
              className={`flex-1 py-3 rounded-lg border-2 transition-all ${
                mode === 't2v'
                  ? 'border-primary-500 bg-primary-500/10 text-white'
                  : 'border-gray-600 text-gray-400 hover:border-gray-500'
              }`}
            >
              <FileText className="w-5 h-5 mx-auto mb-1" />
              <span className="text-sm font-medium">Text to Video</span>
            </button>
            <button
              onClick={() => setMode('i2v')}
              className={`flex-1 py-3 rounded-lg border-2 transition-all ${
                mode === 'i2v'
                  ? 'border-primary-500 bg-primary-500/10 text-white'
                  : 'border-gray-600 text-gray-400 hover:border-gray-500'
              }`}
            >
              <ImageIcon className="w-5 h-5 mx-auto mb-1" />
              <span className="text-sm font-medium">Image to Video</span>
            </button>
          </div>
        </div>

        {/* Prompt Input */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="label">Prompt</label>
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="text-sm text-primary-400 hover:text-primary-300"
            >
              Use Template
            </button>
          </div>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the video you want to generate... Use <S>text<E> for speech."
            className="textarea h-32"
          />
          {showTemplates && (
            <PromptTemplates onSelect={applyTemplate} />
          )}
        </div>

        {/* Image Upload (for I2V mode) */}
        {mode === 'i2v' && (
          <div>
            <label className="label">First Frame Image</label>
            <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-primary-500 transition-colors cursor-pointer">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="cursor-pointer">
                {image ? (
                  <div className="space-y-2">
                    <ImageIcon className="w-12 h-12 mx-auto text-primary-400" />
                    <p className="text-white font-medium">{image.name}</p>
                    <p className="text-sm text-gray-400">Click to change</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="w-12 h-12 mx-auto text-gray-400" />
                    <p className="text-gray-400">Click to upload image</p>
                    <p className="text-xs text-gray-500">PNG, JPG up to 10MB</p>
                  </div>
                )}
              </label>
            </div>
          </div>
        )}

        {/* Advanced Options */}
        <div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-sm text-gray-400 hover:text-white transition-colors"
          >
            <Settings className="w-4 h-4 mr-2" />
            {showAdvanced ? 'Hide' : 'Show'} Advanced Options
          </button>

          {showAdvanced && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              className="mt-4 space-y-4 p-4 bg-gray-700/50 rounded-lg"
            >
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label text-xs">Resolution</label>
                  <select
                    value={options.resolution}
                    onChange={(e) => setOptions({ ...options, resolution: e.target.value })}
                    className="select text-sm"
                  >
                    <option value="720x720">720x720</option>
                    <option value="960x960">960x960</option>
                    <option value="704x1280">704x1280 (9:16)</option>
                    <option value="1280x704">1280x704 (16:9)</option>
                  </select>
                </div>
                <div>
                  <label className="label text-xs">Duration</label>
                  <select
                    value={options.duration}
                    onChange={(e) => setOptions({ ...options, duration: e.target.value })}
                    className="select text-sm"
                  >
                    <option value="5s">5 seconds</option>
                    <option value="10s">10 seconds</option>
                  </select>
                </div>
                <div>
                  <label className="label text-xs">Seed</label>
                  <input
                    type="number"
                    value={options.seed}
                    onChange={(e) => setOptions({ ...options, seed: parseInt(e.target.value) })}
                    className="input text-sm"
                  />
                </div>
                <div>
                  <label className="label text-xs">Steps</label>
                  <input
                    type="number"
                    value={options.steps}
                    onChange={(e) => setOptions({ ...options, steps: parseInt(e.target.value) })}
                    className="input text-sm"
                    min="20"
                    max="100"
                  />
                </div>
                <div>
                  <label className="label text-xs">Video Guidance</label>
                  <input
                    type="number"
                    value={options.videoGuidance}
                    onChange={(e) => setOptions({ ...options, videoGuidance: parseFloat(e.target.value) })}
                    className="input text-sm"
                    step="0.5"
                    min="0"
                    max="10"
                  />
                </div>
                <div>
                  <label className="label text-xs">Audio Guidance</label>
                  <input
                    type="number"
                    value={options.audioGuidance}
                    onChange={(e) => setOptions({ ...options, audioGuidance: parseFloat(e.target.value) })}
                    className="input text-sm"
                    step="0.5"
                    min="0"
                    max="10"
                  />
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          className="btn-primary w-full text-lg py-4"
        >
          <Wand2 className="w-5 h-5 inline-block mr-2" />
          Add to Queue
        </button>
      </div>
    </div>
  );
};

export default VideoGenerator;
