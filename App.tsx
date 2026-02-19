import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { AppState } from './types';
import { Landing } from './components/Landing';
import { LostFlow } from './components/LostFlow';
import { FoundFlow } from './components/FoundFlow';
import { Verification } from './components/Verification';
import { Footer } from './components/Footer';

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>(AppState.LANDING);

  return (
    <div className="min-h-screen flex flex-col">
      <AnimatePresence mode='wait'>
        {appState === AppState.LANDING && (
          <motion.div key="landing" exit={{ opacity: 0 }} className="flex-1">
            <Landing setAppState={setAppState} />
          </motion.div>
        )}
        
        {appState === AppState.LOST_FLOW && (
          <motion.div 
            key="lost" 
            initial={{ opacity: 0, x: 100 }} 
            animate={{ opacity: 1, x: 0 }} 
            exit={{ opacity: 0, x: -100 }}
            className="flex-1"
          >
            <LostFlow setAppState={setAppState} />
          </motion.div>
        )}

        {appState === AppState.FOUND_FLOW && (
          <motion.div 
            key="found" 
            initial={{ opacity: 0, x: -100 }} 
            animate={{ opacity: 1, x: 0 }} 
            exit={{ opacity: 0, x: 100 }}
            className="flex-1"
          >
            <FoundFlow setAppState={setAppState} />
          </motion.div>
        )}

        {appState === AppState.VERIFICATION && (
          <motion.div 
            key="verify" 
            initial={{ opacity: 0, scale: 0.9 }} 
            animate={{ opacity: 1, scale: 1 }} 
            exit={{ opacity: 0 }}
            className="flex-1"
          >
            <Verification setAppState={setAppState} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Only show footer on Landing or if user scrolls down in flows (simplified for demo) */}
      {appState === AppState.LANDING && <Footer />}
    </div>
  );
};

export default App;