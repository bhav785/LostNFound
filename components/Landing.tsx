import React from 'react';
import { motion } from 'framer-motion';
import { Search, MapPin, Watch, Umbrella, Wallet, Key } from 'lucide-react';
import { AppState } from '../types';

interface LandingProps {
  setAppState: (state: AppState) => void;
}

export const Landing: React.FC<LandingProps> = ({ setAppState }) => {
  // Random floating positions for background elements
  const floatingItems = [
    { Icon: Watch, x: '10%', y: '20%', rot: 12, delay: 0 },
    { Icon: Umbrella, x: '85%', y: '15%', rot: -15, delay: 1 },
    { Icon: Wallet, x: '75%', y: '80%', rot: 8, delay: 0.5 },
    { Icon: Key, x: '15%', y: '75%', rot: -20, delay: 1.5 },
  ];

  return (
    <div className="relative w-full h-screen overflow-hidden flex flex-col items-center justify-center p-6">
      
      {/* Background Decor */}
      <div className="absolute inset-0 pointer-events-none opacity-10">
        <svg className="w-full h-full" width="100%" height="100%">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Floating Elements */}
      {floatingItems.map((item, index) => (
        <motion.div
          key={index}
          className="absolute text-[#2d2d2d] opacity-20 hover:opacity-100 hover:scale-110 transition-opacity cursor-pointer"
          style={{ left: item.x, top: item.y }}
          animate={{ 
            y: [0, -15, 0],
            rotate: [item.rot, item.rot - 5, item.rot]
          }}
          transition={{
            duration: 4 + index,
            repeat: Infinity,
            ease: "easeInOut",
            delay: item.delay
          }}
        >
          <item.Icon size={64} strokeWidth={1.5} />
        </motion.div>
      ))}

      {/* Main Content */}
      <div className="z-10 text-center max-w-4xl w-full">
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-12"
        >
            <h1 className="font-display text-6xl md:text-8xl font-bold mb-4 leading-tight text-[#2d2d2d]">
                lost<span className="text-[#e07a5f]">N</span>found
            </h1>
            <div className="relative inline-block">
                <p className="font-hand text-2xl md:text-3xl text-[#5c5c5c] transform -rotate-2">
                    "Where do the lost things go?"
                </p>
                <div className="absolute -bottom-2 right-0 w-full h-1 bg-[#e07a5f] opacity-50 transform rotate-1"></div>
            </div>
        </motion.div>

        <div className="flex flex-col md:flex-row gap-8 justify-center items-center">
            
            {/* I Lost Something Card */}
            <motion.button
                whileHover={{ scale: 1.05, rotate: -2 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setAppState(AppState.LOST_FLOW)}
                className="group relative bg-[#f4f1ea] w-64 h-80 border-2 border-[#2d2d2d] paper-shadow p-6 flex flex-col items-center justify-between"
            >
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-4 h-12 bg-[#e07a5f]/20 transform -rotate-1 z-0"></div>
                <div className="w-16 h-4 bg-[#e07a5f]/20 absolute top-2 rotate-2"></div> {/* Tape look */}
                
                <div className="mt-8 bg-white border border-[#2d2d2d] p-4 rounded-full">
                    <Search size={32} />
                </div>
                <div className="text-center">
                    <h2 className="font-display text-2xl font-bold mb-2">I Lost Something</h2>
                    <p className="font-hand text-lg text-gray-600">Help me remember.</p>
                </div>
                <div className="w-full h-1 border-t border-dashed border-[#2d2d2d] opacity-30"></div>
                <span className="font-bold text-sm uppercase tracking-widest text-[#e07a5f] group-hover:underline">Start Trace</span>
            </motion.button>

            {/* I Found Something Card */}
            <motion.button
                whileHover={{ scale: 1.05, rotate: 2 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setAppState(AppState.FOUND_FLOW)}
                className="group relative bg-[#2d2d2d] w-64 h-80 border-2 border-[#2d2d2d] paper-shadow p-6 flex flex-col items-center justify-between text-[#f4f1ea]"
            >
                <div className="w-16 h-4 bg-white/20 absolute top-2 -rotate-2"></div> {/* Tape look */}
                
                <div className="mt-8 bg-[#f4f1ea] text-[#2d2d2d] border border-[#f4f1ea] p-4 rounded-full">
                    <MapPin size={32} />
                </div>
                <div className="text-center">
                    <h2 className="font-display text-2xl font-bold mb-2">I Found Something</h2>
                    <p className="font-hand text-lg text-gray-400">File an object.</p>
                </div>
                <div className="w-full h-1 border-t border-dashed border-gray-600 opacity-30"></div>
                <span className="font-bold text-sm uppercase tracking-widest text-[#81b29a] group-hover:underline">Submit Evidence</span>
            </motion.button>

        </div>
      </div>
      
    </div>
  );
};