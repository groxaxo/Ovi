import React from 'react';
import { motion } from 'framer-motion';

interface PromptTemplatesProps {
  onSelect: (template: string) => void;
}

const templates = [
  {
    category: 'Nature',
    prompts: [
      'A serene mountain landscape at sunset with golden light cascading over snow-capped peaks. Audio: Gentle wind and distant bird calls.',
      'Ocean waves crashing against rocky cliffs under a stormy sky. Audio: Powerful wave sounds and thunder.',
      'A peaceful forest stream with sunlight filtering through the canopy. Audio: Flowing water and rustling leaves.',
    ],
  },
  {
    category: 'Urban',
    prompts: [
      'Bustling city street at night with neon lights reflecting on wet pavement. Audio: City ambience, traffic, and distant conversations.',
      'Time-lapse of city skyline transitioning from day to night. Audio: Urban soundscape with gradual evening atmosphere.',
      'Futuristic cityscape with flying vehicles and holographic displays. Audio: Sci-fi ambience and distant vehicle hums.',
    ],
  },
  {
    category: 'Abstract',
    prompts: [
      'Colorful liquid paint mixing and swirling in slow motion. Audio: Ambient electronic music.',
      'Geometric shapes morphing and rotating in 3D space with vibrant colors. Audio: Synthetic tones and atmospheric pads.',
      'Particles forming and dissolving into cosmic patterns. Audio: Ethereal soundscape with reverb.',
    ],
  },
  {
    category: 'Character',
    prompts: [
      '<S>Hello! Welcome to the future of video generation.<E> A friendly AI assistant speaking to camera. Audio: Clear speech with subtle background ambience.',
      '<S>This is amazing technology that brings stories to life.<E> Professional presenter in modern studio. Audio: Speech with soft background music.',
      'A cat playing with a ball of yarn in a cozy living room. Audio: Playful meowing and gentle movement sounds.',
    ],
  },
];

const PromptTemplates: React.FC<PromptTemplatesProps> = ({ onSelect }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-2 p-4 bg-gray-700/50 rounded-lg space-y-4 max-h-96 overflow-y-auto"
    >
      {templates.map((category, idx) => (
        <div key={idx}>
          <h3 className="text-sm font-semibold text-primary-400 mb-2">
            {category.category}
          </h3>
          <div className="space-y-2">
            {category.prompts.map((prompt, pIdx) => (
              <button
                key={pIdx}
                onClick={() => onSelect(prompt)}
                className="w-full text-left p-3 bg-gray-800 hover:bg-gray-750 rounded-lg text-sm text-gray-300 hover:text-white transition-all border border-gray-700 hover:border-primary-500"
              >
                {prompt.length > 100 ? prompt.substring(0, 100) + '...' : prompt}
              </button>
            ))}
          </div>
        </div>
      ))}
    </motion.div>
  );
};

export default PromptTemplates;
