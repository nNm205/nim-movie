import { AlertCircle } from "lucide-react";

const ErrorAlert = ({ message }) => {
  if (!message) return null;

  return (
    <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
      <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
      <p className="text-red-400 text-sm">{message}</p>
    </div>
  );
};

export default ErrorAlert;
