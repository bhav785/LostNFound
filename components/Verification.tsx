import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Check, Lock, Unlock, QrCode, Upload, HelpCircle, User, ShieldCheck, AlertCircle } from 'lucide-react';
import { AppState } from '../types';
import { Button } from './ui/Button';

interface VerificationProps {
    setAppState: (state: AppState) => void;
}

enum VerificationStep {
    LOADING = 'LOADING',
    QUESTIONS = 'QUESTIONS',
    UPLOADS = 'UPLOADS',
    OUTCOME = 'OUTCOME'
}

export const Verification: React.FC<VerificationProps> = ({ setAppState }) => {
    const [step, setStep] = useState<VerificationStep>(VerificationStep.LOADING);
    const [matchId, setMatchId] = useState<string | null>(null);
    const [questions, setQuestions] = useState<any[]>([]);
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [itemProof, setItemProof] = useState<File | null>(null);
    const [selfie, setSelfie] = useState<File | null>(null);
    const [status, setStatus] = useState<string>('PENDING'); // PENDING, VERIFIED, MANUAL_REVIEW, FAILED
    const [confidenceScore, setConfidenceScore] = useState<number>(0);
    const [qrUrl, setQrUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

    useEffect(() => {
        const path = window.location.pathname;
        const matchIdMatch = path.match(/\/verify\/(\d+)/);
        const id = matchIdMatch ? matchIdMatch[1] : null;

        if (id) {
            setMatchId(id);
            startVerificationFlow(id);
        } else {
            setError("No match ID identified in the link.");
            setStep(VerificationStep.OUTCOME);
        }
    }, []);

    const startVerificationFlow = async (id: string) => {
        try {
            const res = await fetch(`${baseUrl}/api/verify/start/${id}`);
            const data = await res.json();
            if (data.success) {
                setQuestions(data.questions);
                setStep(VerificationStep.QUESTIONS);
            } else {
                setError(data.message);
                setStep(VerificationStep.OUTCOME);
            }
        } catch (err) {
            setError("Sync error with the archives.");
            setStep(VerificationStep.OUTCOME);
        }
    };

    const handleAnswerChange = (index: number, val: string) => {
        setAnswers(prev => ({ ...prev, [index]: val }));
    };

    const handleSubmitAnswers = () => {
        setStep(VerificationStep.UPLOADS);
    };

    const handleSubmitAll = async () => {
        if (!itemProof || !selfie || !matchId) return;

        setSubmitting(true);
        const formData = new FormData();
        formData.append('item_proof', itemProof);
        formData.append('selfie', selfie);

        const answersList = questions.map((q, idx) => ({
            question: q.question,
            answer: answers[idx] || ""
        }));
        formData.append('answers', JSON.stringify(answersList));

        try {
            const res = await fetch(`${baseUrl}/api/verify/submit/${matchId}`, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (data.success) {
                setStatus(data.status);
                setConfidenceScore(data.confidence_score);
                if (data.qr_url) setQrUrl(data.qr_url);
                setStep(VerificationStep.OUTCOME);
            } else {
                setError(data.message);
                setStep(VerificationStep.OUTCOME);
            }
        } catch (err) {
            setError("Transmission intercepted or failed.");
            setStep(VerificationStep.OUTCOME);
        } finally {
            setSubmitting(false);
        }
    };

    const renderStep = () => {
        switch (step) {
            case VerificationStep.QUESTIONS:
                return (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-lg">
                        <div className="mb-6 flex items-center gap-3">
                            <div className="bg-[#e07a5f]/10 p-2 rounded-full text-[#e07a5f]">
                                <HelpCircle size={24} />
                            </div>
                            <h2 className="font-display text-2xl font-bold text-[#2d2d2d]">Ownership Verification</h2>
                        </div>
                        <p className="font-hand text-gray-500 mb-8">Sherlock needs to confirm few details to ensure this case is closed correctly.</p>

                        <div className="space-y-6 mb-8">
                            {questions.map((q, idx) => (
                                <div key={idx} className="space-y-2">
                                    <label className="block font-display font-bold text-sm text-[#2d2d2d]">{q.question}</label>
                                    <input
                                        type="text"
                                        className="w-full bg-white border-2 border-[#2d2d2d] p-3 font-hand focus:outline-none focus:ring-2 focus:ring-[#e07a5f] transition-all"
                                        placeholder="Your answer..."
                                        value={answers[idx] || ""}
                                        onChange={(e) => handleAnswerChange(idx, e.target.value)}
                                    />
                                </div>
                            ))}
                        </div>

                        <Button
                            className="w-full h-14 bg-[#2d2d2d] text-white font-display font-bold text-lg hover:bg-black transition-colors"
                            onClick={handleSubmitAnswers}
                        >
                            Next: Proof of Submission
                        </Button>
                    </motion.div>
                );

            case VerificationStep.UPLOADS:
                return (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-lg">
                        <div className="mb-6 flex items-center gap-3">
                            <div className="bg-[#81b29a]/10 p-2 rounded-full text-[#81b29a]">
                                <ShieldCheck size={24} />
                            </div>
                            <h2 className="font-display text-2xl font-bold text-[#2d2d2d]">Visual Evidence</h2>
                        </div>
                        <p className="font-hand text-gray-500 mb-8">Securely upload photos to complete the verification protocol.</p>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                            {/* Item Proof */}
                            <div className={`relative border-2 border-[#2d2d2d] border-dashed p-6 flex flex-col items-center justify-center text-center group cursor-pointer hover:bg-white transition-colors ${itemProof ? 'bg-white' : 'bg-[#f4f1ea]'}`}>
                                <input
                                    type="file"
                                    className="absolute inset-0 opacity-0 cursor-pointer"
                                    onChange={(e) => setItemProof(e.target.files?.[0] || null)}
                                />
                                {itemProof ? (
                                    <>
                                        <div className="bg-[#81b29a] text-white p-2 rounded-full mb-2"><Check size={20} /></div>
                                        <span className="text-xs font-bold text-[#2d2d2d] truncate max-w-full">{itemProof.name}</span>
                                    </>
                                ) : (
                                    <>
                                        <Upload size={32} className="text-[#2d2d2d] mb-2 group-hover:scale-110 transition-transform" />
                                        <span className="text-xs font-bold uppercase tracking-widest text-[#2d2d2d]">Item Photo</span>
                                        <span className="text-[10px] text-gray-500 mt-1">Proof of ownership</span>
                                    </>
                                )}
                            </div>

                            {/* Selfie */}
                            <div className={`relative border-2 border-[#2d2d2d] border-dashed p-6 flex flex-col items-center justify-center text-center group cursor-pointer hover:bg-white transition-colors ${selfie ? 'bg-white' : 'bg-[#f4f1ea]'}`}>
                                <input
                                    type="file"
                                    className="absolute inset-0 opacity-0 cursor-pointer"
                                    onChange={(e) => setSelfie(e.target.files?.[0] || null)}
                                />
                                {selfie ? (
                                    <>
                                        <div className="bg-[#81b29a] text-white p-2 rounded-full mb-2"><Check size={20} /></div>
                                        <span className="text-xs font-bold text-[#2d2d2d] truncate max-w-full">{selfie.name}</span>
                                    </>
                                ) : (
                                    <>
                                        <User size={32} className="text-[#2d2d2d] mb-2 group-hover:scale-110 transition-transform" />
                                        <span className="text-xs font-bold uppercase tracking-widest text-[#2d2d2d]">Owner Selfie</span>
                                        <span className="text-[10px] text-gray-500 mt-1">Identity verification</span>
                                    </>
                                )}
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <Button
                                className="flex-1 h-12 border-2 border-[#2d2d2d] text-[#2d2d2d] font-bold"
                                onClick={() => setStep(VerificationStep.QUESTIONS)}
                            >
                                Back
                            </Button>
                            <Button
                                className="flex-[2] h-12 bg-[#2d2d2d] text-white font-bold disabled:opacity-50"
                                onClick={handleSubmitAll}
                                disabled={!itemProof || !selfie || submitting}
                            >
                                {submitting ? "Processing..." : "Submit Verification"}
                            </Button>
                        </div>
                    </motion.div>
                );

            case VerificationStep.OUTCOME:
                return (
                    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="w-full max-w-md">
                        {error ? (
                            <div className="bg-white border-2 border-[#e07a5f] p-8 text-center shadow-[8px_8px_0px_#e07a5f]">
                                <AlertCircle size={48} className="text-[#e07a5f] mx-auto mb-4" />
                                <h3 className="font-display font-bold text-2xl text-[#2d2d2d] mb-2">Protocol Error</h3>
                                <p className="font-hand text-gray-500 mb-6">{error}</p>
                                <Button onClick={() => setAppState(AppState.LANDING)} className="w-full bg-[#2d2d2d] text-white">Return Home</Button>
                            </div>
                        ) : (
                            <div className="bg-white border-2 border-[#2d2d2d] p-8 text-center paper-shadow">
                                {status === 'VERIFIED' ? (
                                    <>
                                        <div className="bg-[#81b29a]/10 p-4 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6 text-[#81b29a]">
                                            <Unlock size={48} />
                                        </div>
                                        <h3 className="font-display font-bold text-3xl text-[#2d2d2d] mb-2">Verified!</h3>
                                        <p className="font-hand text-gray-500 mb-8">Match confirmed with {confidenceScore}% confidence.</p>

                                        <div className="bg-[#2d2d2d] p-6 mb-6 relative overflow-hidden group">
                                            {qrUrl && <img src={qrUrl} alt="Verification QR" className="w-48 h-48 mx-auto relative z-10" />}
                                            <motion.div
                                                className="absolute inset-0 bg-gradient-to-b from-transparent via-[#e07a5f]/20 to-transparent"
                                                animate={{ top: ['-100%', '100%'] }}
                                                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                                            />
                                        </div>
                                        <p className="text-[10px] font-mono uppercase tracking-[0.2em] text-[#2d2d2d]">Present this token at the collection depot</p>
                                    </>
                                ) : status === 'MANUAL_REVIEW' ? (
                                    <>
                                        <div className="bg-yellow-500/10 p-4 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6 text-yellow-600">
                                            <AlertCircle size={48} />
                                        </div>
                                        <h3 className="font-display font-bold text-2xl text-[#2d2d2d] mb-2">Manual Review</h3>
                                        <p className="font-hand text-gray-500 mb-6">Sherlock is unsure. A human detective will review your evidence shortly. Score: {confidenceScore}%</p>
                                    </>
                                ) : (
                                    <>
                                        <div className="bg-[#e07a5f]/10 p-4 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6 text-[#e07a5f]">
                                            <Lock size={48} />
                                        </div>
                                        <h3 className="font-display font-bold text-2xl text-[#2d2d2d] mb-2">Verification Failed</h3>
                                        <p className="font-hand text-gray-500 mb-6">The evidence provided does not match our records. Score: {confidenceScore}%</p>
                                    </>
                                )}
                                <Button onClick={() => setAppState(AppState.LANDING)} className="w-full mt-4 border-2 border-[#2d2d2d] text-[#2d2d2d] font-bold">Close Case</Button>
                            </div>
                        )}
                    </motion.div>
                );

            default:
                return (
                    <div className="flex flex-col items-center">
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                            className="text-[#e07a5f] mb-4"
                        >
                            <Lock size={48} />
                        </motion.div>
                        <p className="font-hand text-gray-500">Decrypting verification link...</p>
                    </div>
                );
        }
    };

    return (
        <div className="w-full min-h-screen bg-[#f4f1ea] flex flex-col items-center justify-center p-6 relative">
            <button
                onClick={() => setAppState(AppState.LANDING)}
                className="absolute top-8 left-8 flex items-center text-[#2d2d2d] hover:underline font-bold"
            >
                <ArrowLeft size={20} className="mr-2" />
                Return to Headquarters
            </button>

            {renderStep()}
        </div>
    );
};
