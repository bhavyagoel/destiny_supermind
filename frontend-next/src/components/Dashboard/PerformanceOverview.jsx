import React, { useState } from 'react';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  BarElement,
  ArcElement,
  Legend,
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';

// Register required Chart.js components
ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, BarElement, ArcElement, Legend);

const PerformanceOverview = () => {
  const [currentChart, setCurrentChart] = useState(0); // Track current chart index

  // Data for Line Chart
  const lineChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Carousel',
        data: [1200, 1900, 1600, 2500, 2200, 2800],
        borderColor: 'rgb(37, 99, 235)', // Blue
        tension: 0.4,
      },
      {
        label: 'Photo',
        data: [500, 800, 600, 1000, 900, 1200],
        borderColor: 'rgb(147, 51, 234)', // Purple
        tension: 0.4,
      },
      {
        label: 'Reels',
        data: [1500, 200, 700, 1100, 1900, 200],
        borderColor: 'rgb(14, 151, 2)', // Green
        tension: 0.4,
      },
      {
        label: 'Videos',
        data: [1300, 2200, 1800, 2300, 2100, 2700],
        borderColor: 'rgb(255, 99, 132)', // Red
        tension: 0.4,
      },
      {
        label: 'Stories',
        data: [700, 1000, 900, 1400, 1100, 1500],
        borderColor: 'rgb(255, 159, 64)', // Orange
        tension: 0.4,
      },
    ],
  };

  // Data for Bar Chart
  const barChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Carousel Views',
        data: [1200, 1900, 1600, 2500, 2200, 2800],
        backgroundColor: 'rgb(37, 99, 235)', // Blue
      },
    ],
  };

  // Data for Pie Chart
  const pieChartData = {
    labels: ['Carousel', 'Photo', 'Reels'],
    datasets: [
      {
        data: [1200, 800, 1500],
        backgroundColor: ['rgb(37, 99, 235)', 'rgb(147, 51, 234)', 'rgb(14, 151, 2)'],
      },
    ],
  };

  // Carousel Functionality
  const handleNextChart = () => {
    setCurrentChart((prev) => (prev + 1) % 3); // Cycle through charts
  };

  const handlePrevChart = () => {
    setCurrentChart((prev) => (prev - 1 + 3) % 3); // Cycle backward through charts
  };

  // Chart rendering based on the currentChart state
  const renderChart = () => {
    switch (currentChart) {
      case 0:
        return <Line data={lineChartData} options={{ responsive: true, maintainAspectRatio: true }} />;
      case 1:
        return <Bar data={barChartData} options={{ responsive: true, maintainAspectRatio: false }} />;
      case 2:
        return <Pie data={pieChartData} options={{ responsive: true }} />;
      default:
        return null;
    }
  };

  return (
    <div className="glass-effect rounded-xl p-6 h-full relative overflow-hidden">
      <h2 className="text-xl font-semibold mb-4">Performance Overview</h2>

      {/* Chart Container with Sliding Effect */}
      <div className="flex justify-center items-center transition-transform duration-500 ease-in-out">
        <div className="w-full h-[375px]">
          {/* Center Pie chart in performance overview space */}
          <div className="flex justify-center items-center h-full">
            {renderChart()}
          </div>
        </div>
      </div>

      {/* Navigation Arrows */}
      <div className="absolute top-1/2 left-0 right-0 flex justify-between transform -translate-y-1/2 px-4">
        <button
          className="bg-gray-800 text-white p-2 rounded-full shadow-lg hover:bg-gray-700"
          onClick={handlePrevChart}
        >
          &#8592;
        </button>
        <button
          className="bg-gray-800 text-white p-2 rounded-full shadow-lg hover:bg-gray-700"
          onClick={handleNextChart}
        >
          &#8594;
        </button>
      </div>
    </div>
  );
};

export default PerformanceOverview;
