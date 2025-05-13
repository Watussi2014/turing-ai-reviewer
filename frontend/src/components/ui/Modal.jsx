import React from 'react';
import { Button } from '@/components/ui/button';

const Modal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="relative bg-[#1a1b1e] rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="absolute top-4 right-4">
          <Button 
            onClick={onClose} 
            variant="ghost" 
            className="h-8 w-8 p-0 rounded-full text-gray-400 hover:text-white hover:bg-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </Button>
        </div>
        <div className="max-h-[90vh] overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;