import Link from "next/link";
import { useRouter } from "next/router";
import { BookOpen, FileText, Home, LogOut, Settings } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const menuItems = [
  { path: "/dashboard", icon: Home, label: "Panel" },
  { path: "/settings", icon: Settings, label: "Configuracion" },
  { path: "/logs", icon: FileText, label: "Registros" },
  { path: "/guide", icon: BookOpen, label: "Guia del usuario" },
];

export default function Sidebar() {
  const router = useRouter();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    void router.push("/login");
  };

  return (
    <div className="flex h-screen w-64 flex-col bg-gradient-to-b from-slate-800 via-blue-700 to-slate-800 text-white shadow-2xl">
      <div className="border-b border-blue-800/50 p-4 text-center text-lg font-semibold">Car Scraper</div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = router.pathname === item.path;
            return (
              <li key={item.path}>
                <Link
                  href={item.path}
                  className={`flex items-center space-x-3 rounded-lg px-4 py-3 transition-all ${
                    active ? "bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg" : "hover:bg-white/10"
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="border-t border-blue-800/50 p-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center space-x-3 rounded-lg px-4 py-3 text-left transition-all hover:bg-red-600/20"
        >
          <LogOut size={20} />
          <span className="font-medium">Cerrar sesion</span>
        </button>
      </div>
    </div>
  );
}
