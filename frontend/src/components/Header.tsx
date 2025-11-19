import React from 'react';
import { Video, Sparkles } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-gray-800/50 backdrop-blur-lg border-b border-gray-700 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Video className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white flex items-center">
                Ovi Studio
                <Sparkles className="w-4 h-4 ml-2 text-yellow-400" />
              </h1>
              <p className="text-xs text-gray-400">AI Video Generation</p>
            </div>
          </div>

          {/* Nav Items */}
          <nav className="flex items-center space-x-6">
            <button className="text-gray-300 hover:text-white transition-colors">
              Gallery
            </button>
            <button className="text-gray-300 hover:text-white transition-colors">
              Settings
            </button>
            <button className="btn-primary text-sm">
              Get Started
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
