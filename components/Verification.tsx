import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Check, Lock, Unlock, QrCode } from 'lucide-react';
import { AppState } from '../types';
import { Button } from './ui/Button';

interface VerificationProps {
    setAppState: (state: AppState) => void;
}

export const Verification: React.FC<VerificationProps> = ({ setAppState }) => {
    const [progress, setProgress] = useState(0);
    const [matchData, setMatchData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

    useEffect(() => {
        // Check for match_id in URL
        const path = window.location.pathname;
        const matchIdMatch = path.match(/\/verify\/(\d+)/);
        const matchId = matchIdMatch ? matchIdMatch[1] : null;

        if (matchId) {
            const fetchMatch = async () => {
                try {
                    const res = await fetch(`${baseUrl}/api/verify/${matchId}`);
                    const data = await res.json();
                    if (data.success) {
                        setMatchData(data.match);
                    } else {
                        setError(data.message);
                    }
                } catch (err) {
                    setError("Connection to archives lost.");
                } finally {
                    setLoading(false);
                }
            };
            fetchMatch();
        } else {
            setLoading(false);
        }

        // Simulate timeline progress
        const timer = setInterval(() => {
            setProgress(prev => {
                if (prev >= 4) {
                    clearInterval(timer);
                    return 4;
                }
                return prev + 1;
            });
        }, 1500);
        return () => clearInterval(timer);
    }, []);

    const steps = [
        { id: 1, text: "Smart Match Detected", sub: "Analysis of 42 data points" },
        { id: 2, text: "Owner Notified", sub: "Secure channel established" },
        { id: 3, text: "Fraud Logic Check", sub: "Behavioral consistency verified" },
        { id: 4, text: "Identity Confirmed", sub: "Ready for retrieval" }
    ];

    return (
        <div className="w-full min-h-screen bg-[#f4f1ea] flex flex-col items-center justify-center p-6">

            <button
                onClick={() => setAppState(AppState.LANDING)}
                className="absolute top-8 left-8 flex items-center text-[#2d2d2d] hover:underline font-bold"
            >
                <ArrowLeft size={20} className="mr-2" />
                Close Case
            </button>

            <div className="max-w-4xl w-full flex flex-col md:flex-row gap-12 items-center">

                {/* Timeline */}
                <div className="flex-1 w-full">
                    <h2 className="font-display text-3xl font-bold mb-8 text-[#2d2d2d]">Verification Protocol</h2>
                    <div className="relative">
                        {/* Vertical Line */}
                        <div className="absolute left-4 top-0 bottom-0 w-1 bg-[#d4d4d4]"></div>

                        <div className="space-y-8">
                            {steps.map((step, idx) => {
                                const isActive = progress >= idx + 1;
                                const isPast = progress > idx + 1;

                                return (
                                    <motion.div
                                        key={step.id}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: isActive ? 1 : 0.4, x: 0 }}
                                        className="flex items-start relative pl-12"
                                    >
                                        {/* Dot */}
                                        <div className={`absolute left-2.5 -translate-x-1/2 w-4 h-4 rounded-full border-2 border-[#f4f1ea] z-10 transition-colors duration-500 ${isActive ? 'bg-[#2d2d2d]' : 'bg-[#d4d4d4]'}`}>
                                            {isActive && <motion.div layoutId="glow" className="absolute inset-0 rounded-full bg-[#e07a5f] opacity-50 blur-sm" />}
                                        </div>

                                        <div>
                                            <h3 className={`font-display font-bold text-lg ${isActive ? 'text-[#2d2d2d]' : 'text-gray-400'}`}>
                                                {step.text}
                                            </h3>
                                            <p className="font-hand text-gray-500">{step.sub}</p>
                                        </div>

                                        {isActive && (
                                            <motion.div
                                                initial={{ scale: 0 }} animate={{ scale: 1 }}
                                                className="ml-auto text-[#81b29a]"
                                            >
                                                <Check size={20} />
                                            </motion.div>
                                        )}
                                    </motion.div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* The Result Card */}
                <div className="flex-1 w-full flex justify-center">
                    <AnimatePresence mode='wait'>
                        {progress < 4 ? (
                            <motion.div
                                key="locked"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9, rotate: 10 }}
                                className="w-64 h-80 bg-[#2d2d2d] rounded-sm paper-shadow border-2 border-[#2d2d2d] flex flex-col items-center justify-center text-[#f4f1ea]"
                            >
                                <div className="mb-6 relative">
                                    <Lock size={48} className="text-[#e07a5f]" />
                                    <div className="absolute inset-0 bg-[#e07a5f] blur-xl opacity-20"></div>
                                </div>
                                <h3 className="font-display font-bold text-xl uppercase tracking-widest mb-2">Processing</h3>
                                <p className="font-hand text-gray-400 text-sm">Verifying data...</p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="unlocked"
                                initial={{ opacity: 0, scale: 0.9, rotate: -5 }}
                                animate={{ opacity: 1, scale: 1, rotate: 0 }}
                                className="w-72 h-auto bg-white rounded-sm paper-shadow border-2 border-[#2d2d2d] p-6 relative"
                            >
                                <div className="w-24 h-6 bg-[#81b29a]/30 absolute -top-3 left-1/2 -translate-x-1/2 rotate-1"></div>

                                <div className="flex flex-col items-center text-center">
                                    <div className="bg-[#81b29a]/10 p-4 rounded-full mb-4 text-[#81b29a]">
                                        <Unlock size={32} />
                                    </div>
                                    <h3 className="font-display font-bold text-2xl text-[#2d2d2d] mb-1">Claim Verified</h3>
                                    <p className="font-hand text-gray-500 text-sm mb-6">Match found with {matchData?.similarity || 90}% confidence.</p>

                                    {matchData && (
                                        <div className="w-full mb-6 text-left space-y-3 bg-[#f4f1ea] p-4 border border-dashed border-[#2d2d2d]">
                                            <div>
                                                <span className="block text-[10px] uppercase font-bold text-[#e07a5f]">Your Description</span>
                                                <p className="font-hand leading-tight text-sm">{matchData.lost_description}</p>
                                            </div>
                                            <div className="border-t border-gray-300 pt-2">
                                                <span className="block text-[10px] uppercase font-bold text-[#81b29a]">Found Item</span>
                                                <p className="font-hand leading-tight text-sm">{matchData.found_caption}</p>
                                            </div>
                                            <div className="h-32 rounded-sm overflow-hidden border border-[#2d2d2d]">
                                                <img src={matchData.found_image_url.replace("http://localhost:8000", baseUrl)} alt="Matched item" className="w-full h-full object-cover" />
                                            </div>
                                        </div>
                                    )}

                                    <div className="w-full aspect-square bg-[#2d2d2d] p-4 flex items-center justify-center mb-4 relative group cursor-pointer overflow-hidden">
                                        <QrCode size={120} className="text-white relative z-10" />
                                        <motion.div
                                            className="absolute inset-0 bg-gradient-to-b from-transparent via-[#e07a5f]/30 to-transparent"
                                            animate={{ top: ['-100%', '100%'] }}
                                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                        />
                                    </div>
                                    <p className="text-xs font-mono uppercase tracking-widest text-[#2d2d2d]">Show at Depot: {matchData?.found_location || "Central Archives"}</p>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};