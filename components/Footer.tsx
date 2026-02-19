import React from 'react';
import { motion } from 'framer-motion';

export const Footer: React.FC = () => {
  const stories = [
    { title: "The Red Scarf", desc: "Reunited after 11 days of winter.", color: "bg-[#e07a5f]" },
    { title: "Vintage Leica", desc: "Returned by a Helpful Citizen.", color: "bg-[#2d2d2d]" },
    { title: "Child's Bear", desc: "Found at Central Station.", color: "bg-[#81b29a]" },
  ];

  return (
    <footer className="w-full py-16 px-6 bg-[#e8e4db] border-t-2 border-[#2d2d2d] overflow-hidden">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center space-x-4 mb-8">
            <h3 className="font-display font-bold text-xl uppercase tracking-widest text-[#2d2d2d]">Lost Stories Wall</h3>
            <div className="h-0.5 flex-1 bg-[#2d2d2d] opacity-20"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {stories.map((story, i) => (
                <motion.div 
                    key={i}
                    whileHover={{ y: -5, rotate: i % 2 === 0 ? 1 : -1 }}
                    className="bg-white p-4 paper-shadow-sm border border-[#2d2d2d] transform rotate-1"
                >
                    <div className={`w-full h-32 ${story.color} mb-4 flex items-center justify-center opacity-90`}>
                        {/* Abstract Illustration Placeholder */}
                        <div className="w-12 h-12 bg-white/20 rounded-full"></div>
                    </div>
                    <h4 className="font-display font-bold text-lg mb-1">{story.title}</h4>
                    <p className="font-hand text-gray-600 text-lg leading-tight">{story.desc}</p>
                </motion.div>
            ))}
        </div>

        <div className="mt-16 text-center">
            <p className="font-hand text-2xl text-[#2d2d2d]">"Not everything lost is gone."</p>
            <p className="text-xs font-mono text-gray-400 mt-4 uppercase tracking-widest">© 2024 lostNfound Collective</p>
        </div>
      </div>
    </footer>
  );
};