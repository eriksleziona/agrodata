import React from "react";
import { Loader2 } from "lucide-react";

export interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeMap = {
  sm: "w-4 h-4",
  md: "w-6 h-6",
  lg: "w-10 h-10",
};

export const Spinner: React.FC<SpinnerProps> = ({
  size = "md",
  className = "",
}) => {
  return (
    <Loader2
      className={`animate-spin text-agro-600 ${sizeMap[size]} ${className}`}
    />
  );
};

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = "",
  ...props
}) => {
  return (
    <div
      className={`animate-pulse rounded-md bg-slate-200/80 ${className}`}
      {...props}
    />
  );
};

export interface PageLoadingProps {
  message?: string;
}

export const PageLoading: React.FC<PageLoadingProps> = ({
  message = "Loading AgroData...",
}) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full py-12 space-y-4">
      <Spinner size="lg" />
      <p className="text-sm font-medium text-slate-500 animate-pulse">
        {message}
      </p>
    </div>
  );
};
