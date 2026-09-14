import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Warehouse,
  Grid3X3,
  Tractor,
  ClipboardList,
  Sprout,
  ChevronRight,
} from "lucide-react";
import { useAuthStore } from "../../store/useAuthStore";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

const navigation: NavItem[] = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Farms", href: "/farms", icon: Warehouse },
  { name: "Fields", href: "/fields", icon: Grid3X3 },
  { name: "Machines", href: "/machines", icon: Tractor },
  { name: "Jobs", href: "/jobs", icon: ClipboardList },
];

export const Sidebar: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 h-screen sticky top-0 border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-slate-800/80 bg-slate-950/40">
        <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-agro-500 to-agro-700 flex items-center justify-center text-white shadow-md shadow-agro-900/30">
          <Sprout className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-white text-base tracking-tight leading-none">
            AgroData
          </h1>
          <span className="text-[10px] font-medium tracking-wider text-agro-400 uppercase">
            Farm Telemetry OS
          </span>
        </div>
      </div>

      {/* Organization Badge */}
      <div className="px-5 py-3.5 border-b border-slate-800/60 bg-slate-950/20">
        <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
          Tenant Workspace
        </div>
        <div className="flex items-center justify-between text-xs text-slate-300 font-medium">
          <span
            className="truncate max-w-[170px]"
            title={user?.organization_id || "Organization"}
          >
            Org #{user?.organization_id?.slice(0, 8)}...
          </span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-agro-950 text-agro-300 border border-agro-800/60">
            {user?.role || "Active"}
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all group ${
                  isActive
                    ? "bg-agro-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-5 h-5 transition-colors ${
                        isActive
                          ? "text-white"
                          : "text-slate-400 group-hover:text-slate-200"
                      }`}
                    />
                    <span>{item.name}</span>
                  </div>
                  {isActive && <ChevronRight className="w-4 h-4 opacity-70" />}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/30 text-center">
        <p className="text-[11px] text-slate-500">
          AgroData Platform &copy; 2026
        </p>
        <p className="text-[10px] text-slate-600">v0.1.0-foundation</p>
      </div>
    </aside>
  );
};
