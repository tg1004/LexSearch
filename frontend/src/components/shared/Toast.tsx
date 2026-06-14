import { CheckCircle, X } from 'lucide-react';
import { useEffect } from 'react';

interface ToastProps {
  message: string;
  onClose: () => void;
  duration?: number;
}

export default function Toast({ message, onClose, duration = 3000 }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-primary text-white rounded-lg shadow-lg">
      <CheckCircle className="w-5 h-5 text-green-400" />
      <span className="text-sm">{message}</span>
      <button onClick={onClose} className="ml-2 hover:opacity-70" aria-label="Close">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
