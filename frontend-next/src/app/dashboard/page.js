'use client'

import Navbar from "../../components/Dashboard/Navbar";
import PerformanceOverview from "../../components/Dashboard/PerformanceOverview";
import AIChat from "../../components/Dashboard/AIChat";
import MetricCard from "../../components/Dashboard/MetricCard";

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <main className="pt-20 px-4 lg:px-8 h-screen flex flex-col lg:flex-row gap-6">
        {/* Left Section */}
        <div className="lg:w-3/4 flex flex-col gap-6 h-full">
          <PerformanceOverview />
          <div className="flex space-x-6">
            <MetricCard title="Followers" value="10k" color="text-blue-600" />
            <MetricCard title="Likes" value="12.5k" color="text-green-600" />
            <MetricCard title="Comments" value="2.3k" color="text-yellow-600" />
            <MetricCard title="Shares" value="1.5k" color="text-red-600" />
          </div>
        </div>

        {/* Right Section */}
        <div className="lg:w-1/4 flex-shrink-0 h-full">
          <AIChat />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
