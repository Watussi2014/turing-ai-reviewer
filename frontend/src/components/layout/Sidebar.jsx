
    import React from 'react';
    import { Home, BarChart3, CalendarDays, ChevronRight, CheckCircle } from 'lucide-react';
    import { Button } from '@/components/ui/button';
    import NavItem from '@/components/common/NavItem';

    const Sidebar = () => (
      <aside className="w-80 bg-[#2C2F3A] text-gray-300 p-6 flex flex-col justify-between min-h-screen">
        <div>
          <div className="flex items-center mb-10">
            <h1 className="text-2xl font-bold text-white">Turing College</h1>
          </div>
          <nav>
            <ul>
              <li className="mb-4">
                <a href="#" className="flex items-center p-2 rounded-lg hover:bg-gray-700 transition-colors">
                  <Home size={20} className="mr-3" /> Course
                </a>
              </li>
              <li className="mb-4">
                <a href="#" className="flex items-center p-2 rounded-lg hover:bg-gray-700 transition-colors">
                  <BarChart3 size={20} className="mr-3" /> Endorsement
                </a>
              </li>
              <li className="mb-4">
                <a href="#" className="flex items-center p-2 rounded-lg hover:bg-gray-700 transition-colors">
                  <CalendarDays size={20} className="mr-3" /> Calendar
                </a>
              </li>
            </ul>
          </nav>
          <div className="mt-10">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Module</span>
              <ChevronRight size={16} />
            </div>
            <h2 className="text-xl font-semibold text-white mb-6">Statistical Inference</h2>
            <div className="space-y-3">
              {['Sprint 1', 'Sprint 2', 'Sprint 3'].map((sprint, index) => (
                <Button
                  key={sprint}
                  variant={index === 1 ? 'default' : 'outline'}
                  className={`w-full justify-start ${index === 1 ? 'bg-indigo-600 hover:bg-indigo-700 text-white' : 'border-gray-600 text-gray-400 hover:bg-gray-700 hover:text-white'}`}
                >
                  {sprint}
                </Button>
              ))}
            </div>
          </div>
          <div className="mt-8">
            <NavItem title="Overview & Probability Distributions" done part="Part 1" />
            <NavItem title="Confidence Intervals & Bayesian Inference" done part="Part 2" />
            <NavItem title="Controlled Experiments and Hypothesis Testing" done part="Part 3" />
            <NavItem title="A/B Testing" done part="Part 4" />
            <NavItem title="Project - Analyzing A/B Tests" project inProgress />
          </div>
        </div>
        <div className="mt-auto text-sm text-gray-500">
          Started on April 30
        </div>
      </aside>
    );

    export default Sidebar;
  