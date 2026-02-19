import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'accent';
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', className = '', ...props }) => {
  const baseStyle = "font-display font-bold uppercase tracking-wide px-6 py-3 border-2 border-[#2d2d2d] transition-all duration-200 active:translate-y-1 active:translate-x-1 active:shadow-none";
  
  const variants = {
    primary: "bg-[#2d2d2d] text-[#f4f1ea] paper-shadow hover:bg-[#404040]",
    secondary: "bg-[#f4f1ea] text-[#2d2d2d] paper-shadow hover:bg-white",
    accent: "bg-[#e07a5f] text-[#f4f1ea] paper-shadow hover:bg-[#e78c73]"
  };

  return (
    <button className={`${baseStyle} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
};