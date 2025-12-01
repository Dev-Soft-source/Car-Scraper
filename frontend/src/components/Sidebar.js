import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Home, Settings, FileText, BookOpen, LogOut } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { path: '/dashboard', icon: Home, label: 'Panel' },
    { path: '/settings', icon: Settings, label: 'Configuración' },
    { path: '/logs', icon: FileText, label: 'Registros' },
    { path: '/guide', icon: BookOpen, label: 'Guía del usuario' },
  ];

  return (
    <div className="h-screen w-64 bg-gradient-to-b from-slate-800 via-blue-700 to-slate-800 text-white flex flex-col shadow-2xl">
      {/* Logo */}
      <div className="border-b border-blue-800/50">
        <div className="flex items-center space-x-10">
            <img 
            src="/logo1.png"
            alt="Logo"
            className="w-full h-[150px]"
          />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 pt-15">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg transform scale-105'
                      : 'hover:bg-white/10'
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

      {/* Logout */}
      <div className="p-4 border-t border-blue-800/50">
        <button
          onClick={handleLogout}
          data-testid="logout-button"
          className="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-red-600/20 transition-all duration-200 w-full text-left"
        >
          <LogOut size={20} />
          <span className="font-medium">Cerrar sesión</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
