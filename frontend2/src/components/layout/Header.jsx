
    import React from 'react';
    import { Users, HelpCircle, Settings } from 'lucide-react';

    const Header = () => (
      <header className="flex items-center justify-end p-6 border-b border-gray-700">
        <div className="flex items-center space-x-4">
          <Users size={20} className="text-gray-400 hover:text-white cursor-pointer" />
          <HelpCircle size={20} className="text-gray-400 hover:text-white cursor-pointer" />
          <Settings size={20} className="text-gray-400 hover:text-white cursor-pointer" />
          <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
            A
          </div>
        </div>
      </header>
    );

    export default Header;
  