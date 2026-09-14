import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "./Button";

export interface ErrorAlertProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  title,
  message,
  onRetry,
  className = "",
}) => {
  return (
    <div
      className={`flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-red-900 ${className}`}
    >
      <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
      <div className="flex-1 text-sm">
        {title && (
          <h4 className="font-semibold text-red-950 mb-0.5">{title}</h4>
        )}
        <p className="text-red-700">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-xs font-semibold text-red-700 hover:text-red-950 underline shrink-0 cursor-pointer"
        >
          Retry
        </button>
      )}
    </div>
  );
};

export interface PageErrorProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const PageError: React.FC<PageErrorProps> = ({
  title = "Something went wrong",
  message = "Failed to load data from the server. Please check your connection and try again.",
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full py-12 px-4 text-center">
      <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center text-red-600 mb-4">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-md mb-6">{message}</p>
      {onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          leftIcon={<RefreshCw className="w-4 h-4" />}
        >
          Try Again
        </Button>
      )}
    </div>
  );
};
