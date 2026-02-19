import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Upload,
  MapPin,
  CheckCircle,
  Shield,
  Award,
} from "lucide-react";
import { AppState } from "../types";
import { Button } from "./ui/Button";

interface FoundFlowProps {
  setAppState: (state: AppState) => void;
}

export const FoundFlow: React.FC<FoundFlowProps> = ({ setAppState }) => {
  const [step, setStep] = useState(1);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    setSelectedFile(file);
    setStep(2);
  };
  const handleSubmit = async () => {
    if (!selectedFile) {
      alert("Please upload an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/found/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log(data);

      setResult(data);
      setStep(3);
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  return (
    <div className="w-full min-h-screen bg-[#2d2d2d] text-[#f4f1ea] p-6 md:p-12 relative">
      {/* Header */}
      <div className="flex items-center justify-between mb-12 max-w-5xl mx-auto">
        <button
          onClick={() => setAppState(AppState.LANDING)}
          className="flex items-center text-[#f4f1ea] hover:text-[#e07a5f] font-bold transition-colors"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Hub
        </button>
        <div className="flex items-center space-x-2">
          <Shield size={20} className="text-[#81b29a]" />
          <span className="font-display font-bold uppercase tracking-wider text-sm text-[#81b29a]">
            Secure Submission Protocol
          </span>
        </div>
      </div>

      <div className="max-w-5xl mx-auto flex flex-col md:flex-row gap-12">
        {/* Left: The "Crate" / Form */}
        <div className="flex-1">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="mb-8"
          >
            <h2 className="font-display text-4xl font-bold mb-4">
              Evidence Locker
            </h2>
            <p className="font-hand text-xl text-gray-400">
              Securely deposit found item details.
            </p>
          </motion.div>

          {step === 1 && (
            <div
              className={`relative w-full h-80 border-4 border-dashed rounded-lg flex flex-col items-center justify-center transition-all cursor-pointer group ${
                dragActive
                  ? "border-[#e07a5f] bg-[#e07a5f]/10"
                  : "border-[#5c5c5c] hover:border-[#f4f1ea]"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
            >
              <div className="bg-[#f4f1ea] text-[#2d2d2d] p-6 rounded-full mb-4 group-hover:scale-110 transition-transform">
                <Upload size={32} />
              </div>
              <h3 className="font-display font-bold text-xl mb-2">
                Drop Item Image Here
              </h3>
              <p className="font-hand text-gray-400">
                or click to open evidence bag
              </p>
              <input
                type="file"
                ref={fileInputRef}
                hidden
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    setSelectedFile(file);
                    setStep(2);
                  }
                }}
              />

              {/* Decorative Crate Texture */}
              <div
                className="absolute top-0 left-0 w-full h-full pointer-events-none opacity-5"
                style={{
                  backgroundImage:
                    "repeating-linear-gradient(45deg, #000 0, #000 1px, transparent 0, transparent 50%)",
                  backgroundSize: "10px 10px",
                }}
              ></div>
            </div>
          )}

          {step === 2 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-[#3d3d3d] border-2 border-[#5c5c5c] p-8 rounded-sm paper-shadow"
            >
              <div className="space-y-6">
                <div>
                  <label className="block font-display font-bold text-sm uppercase mb-2 text-[#81b29a]">
                    Location Found
                  </label>
                  <div className="flex bg-[#2d2d2d] border border-[#5c5c5c] p-3 rounded-sm">
                    <MapPin size={20} className="text-gray-400 mr-2" />
                    <input
                      type="text"
                      placeholder="e.g. Central Park Bench"
                      className="bg-transparent w-full outline-none text-[#f4f1ea] font-hand text-lg"
                    />
                  </div>
                </div>
                <div>
                  <label className="block font-display font-bold text-sm uppercase mb-2 text-[#e07a5f]">
                    Condition Notes
                  </label>
                  <textarea
                    rows={3}
                    className="w-full bg-[#2d2d2d] border border-[#5c5c5c] p-3 rounded-sm outline-none text-[#f4f1ea] font-hand text-lg"
                    placeholder="Any scratches? Wet? Damaged?"
                  ></textarea>
                </div>
                <Button
                  variant="accent"
                  className="w-full"
                  onClick={handleSubmit}
                >
                  Log Into Archive
                </Button>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12 border-2 border-[#81b29a] bg-[#81b29a]/10 rounded-lg"
            >
              <div className="inline-block p-4 bg-[#81b29a] text-[#2d2d2d] rounded-full mb-4">
                <CheckCircle size={48} />
              </div>
              <h3 className="font-display text-3xl font-bold mb-2">
                Evidence Secured
              </h3>
              <p className="font-hand text-xl mb-6">
                You've earned 50 Trust Points.
              </p>
              <Button
                variant="secondary"
                onClick={() => setAppState(AppState.LANDING)}
              >
                Return to Hub
              </Button>
            </motion.div>
          )}
        </div>

        {/* Right: Gamified Trust Wall */}
        <div className="w-full md:w-1/3">
          <div className="bg-[#f4f1ea] text-[#2d2d2d] p-6 rounded-sm rotate-1 paper-shadow border-2 border-[#2d2d2d]">
            <div className="flex items-center justify-between mb-6 border-b-2 border-[#2d2d2d] pb-4">
              <h3 className="font-display font-bold text-xl uppercase">
                Citizen Record
              </h3>
              <Award size={24} className="text-[#e07a5f]" />
            </div>

            <div className="space-y-6">
              <div className="text-center">
                <span className="block font-display text-5xl font-bold text-[#2d2d2d]">
                  850
                </span>
                <span className="font-hand text-gray-500">Trust Points</span>
              </div>

              <div className="space-y-3">
                <h4 className="font-bold font-display text-sm uppercase">
                  Badges Earned
                </h4>
                <div className="grid grid-cols-3 gap-2">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="aspect-square bg-[#e8e4db] border border-[#2d2d2d] rounded-full flex items-center justify-center hover:scale-110 transition-transform cursor-help"
                      title="Helpful Citizen"
                    >
                      <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#e07a5f] to-[#f2cc8f]"></div>
                    </div>
                  ))}
                  <div className="aspect-square border-2 border-dashed border-gray-400 rounded-full flex items-center justify-center opacity-50">
                    <span className="text-xs font-bold text-gray-400">?</span>
                  </div>
                </div>
              </div>

              <div className="bg-[#2d2d2d] text-[#f4f1ea] p-4 rounded-sm mt-4 relative overflow-hidden">
                <div className="relative z-10">
                  <span className="text-xs font-bold text-[#81b29a] uppercase mb-1 block">
                    Current Impact
                  </span>
                  <p className="font-hand text-lg">
                    "You reunited 3 items this month."
                  </p>
                </div>
                <div className="absolute right-0 bottom-0 w-16 h-16 bg-[#81b29a] rounded-full blur-xl opacity-20 transform translate-x-4 translate-y-4"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
