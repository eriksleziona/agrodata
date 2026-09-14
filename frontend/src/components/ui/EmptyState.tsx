import React from "react";
import { PackageOpen } from "lucide-react";
import { Button } from "./Button";

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionText,
  onAction,
  className = "",
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-12 text-center ${className}`}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-slate-400 mb-4 ring-8 ring-slate-50">
        {icon || <PackageOpen className="w-7 h-7" />}
      </div>
      <h3 className="text-base font-semibold text-slate-800">{title}</h3>
      <p className="mt-1.5 text-xs text-slate-500 max-w-sm leading-relaxed">
        {description}
      </p>
      {actionText && onAction && (
        <div className="mt-6">
          <Button variant="primary" size="sm" onClick={onAction}>
            {actionText}
          </Button>
        </div>
      )}
    </div>
  );
};
