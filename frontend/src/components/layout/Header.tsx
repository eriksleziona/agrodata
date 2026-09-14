import React from "react";
import { LogOut, UserCircle, ShieldCheck } from "lucide-react";
import { useAuthStore } from "../../store/useAuthStore";
import { Button } from "../ui/Button";

export const Header: React.FC = () => {
  const { user, logout } = useAuthStore();

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-8 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-100" />
          <span className="text-xs font-medium text-slate-500">
            System Online
          </span>
        </div>
      </div>

      <div className="flex items-center gap-5">
        {/* User Profile Info */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
          <div className="h-9 w-9 rounded-full bg-agro-100 text-agro-700 flex items-center justify-center font-bold text-sm border border-agro-200">
            {user?.first_name ? (
              user.first_name[0]
            ) : (
              <UserCircle className="w-5 h-5" />
            )}
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-semibold text-slate-800 leading-none">
              {user
                ? `${user.first_name} ${user.last_name}`
                : "Authenticated User"}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-agro-600" />
              <span>{user?.role || "OPERATOR"}</span>
              <span className="text-slate-300">•</span>
              <span className="truncate max-w-[120px]">{user?.email}</span>
            </div>
          </div>
        </div>

        {/* Logout Action */}
        <Button
          variant="outline"
          size="sm"
          onClick={logout}
          leftIcon={<LogOut className="w-4 h-4 text-slate-500" />}
          className="text-xs hover:text-red-600 hover:border-red-200"
        >
          Logout
        </Button>
      </div>
    </header>
  );
};
