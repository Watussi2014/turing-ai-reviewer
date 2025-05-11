
    import React from 'react';
    import { CheckCircle, RefreshCw } from 'lucide-react';

    const NavItem = ({ title, done, part, passed, project, inProgress }) => (
      <div className={`mb-3 p-3 rounded-lg ${passed ? 'bg-green-800/30 border border-green-600' : inProgress ? 'bg-yellow-800/30 border border-yellow-600' : 'hover:bg-gray-700/50'}`}>
        <h3 className={`font-medium ${passed ? 'text-green-400' : inProgress ? 'text-yellow-400' : 'text-gray-300'}`}>{title}</h3>
        <div className="flex items-center text-sm mt-1">
          {done && !passed && !inProgress && <CheckCircle size={16} className="text-green-500 mr-2" />}
          {passed && <CheckCircle size={16} className="text-green-400 mr-2" />}
          {inProgress && <RefreshCw size={16} className="text-yellow-400 mr-2 animate-spin" />}
          <span className={passed ? 'text-green-400' : inProgress ? 'text-yellow-400' : 'text-gray-400'}>
            {done && !passed && !inProgress && "Done "}
            {passed && "Passed "}
            {inProgress && "In Progress "}
            {project ? "Project" : part}
          </span>
        </div>
      </div>
    );

    export default NavItem;
  