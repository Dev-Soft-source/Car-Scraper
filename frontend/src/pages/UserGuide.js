import React from 'react';
import { Settings, Play, Filter, BarChart3, Bell } from 'lucide-react';

const UserGuide = () => {
  return (
    <div data-testid="user-guide-page" className="max-w-4xl">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">User Guide</h1>

      <div className="space-y-6">
        {/* Introduction */}
        <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
          <h2 className="text-2xl font-bold mb-3">Welcome to Wallapop Scraper!</h2>
          <p className="text-blue-100">
            This application automatically scrapes Wallapop listings based on your criteria and alerts you
            when items are priced below your target. Follow this guide to get started.
          </p>
        </div>

        {/* Getting Started */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-xl font-bold text-blue-600">1</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900">Configure Your Search</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Navigate to <strong>Settings</strong> and create a new search:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>Give your search a descriptive name</li>
              <li>Specify criteria: make, model, year range, price range, location, etc.</li>
              <li>Set your <strong>target price</strong> - you'll be alerted when listings fall below this</li>
              <li>Choose if you want to track private sellers, professional sellers, or both</li>
              <li>Mark the search as active to include it in scraping</li>
            </ul>
          </div>
        </div>

        {/* Scraping Settings */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Settings className="text-purple-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Configure Scraping Settings</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>In the <strong>Settings</strong> page, configure:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li><strong>Scraping Interval:</strong> How often to check for new listings (in minutes)</li>
              <li><strong>Keywords:</strong> General search terms to filter listings</li>
              <li><strong>Price Range:</strong> Minimum and maximum price boundaries</li>
              <li><strong>Site URLs:</strong> Add Wallapop URLs or other marketplace URLs to scrape</li>
            </ul>
          </div>
        </div>

        {/* Start Scraping */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Play className="text-green-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Start Scraping</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>On the <strong>Dashboard</strong>:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>Select an active search from the dropdown</li>
              <li>Click the <strong>Start Scraper</strong> button to begin collecting listings</li>
              <li>The scraper runs in the background based on your configured interval</li>
              <li>Click <strong>Stop Scraper</strong> to pause scraping</li>
              <li>Use the <strong>Refresh</strong> button to manually update listings</li>
            </ul>
          </div>
        </div>

        {/* Filtering & Sorting */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Filter className="text-orange-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Filter and Sort Results</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Use the filter panel to refine your results:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li><strong>Search:</strong> Find listings by keyword</li>
              <li><strong>Make/Model:</strong> Filter by vehicle make and model</li>
              <li><strong>Price Range:</strong> Set min/max price filters</li>
              <li><strong>Location:</strong> Filter by geographic location</li>
              <li><strong>Seller Type:</strong> Show only private or professional sellers</li>
              <li><strong>Below Target Price Only:</strong> Show only listings meeting your price target</li>
              <li><strong>Sort:</strong> Order by price or date (newest/oldest first)</li>
            </ul>
          </div>
        </div>

        {/* Alerts & Notifications */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Bell className="text-red-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Alerts & Notifications</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Get notified when great deals appear:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>Listings below your target price are highlighted with a green badge</li>
              <li>A sound alert plays when new below-target listings are found</li>
              <li>Browser notifications appear (ensure you've granted permission)</li>
              <li>Check the dashboard regularly for the latest finds</li>
            </ul>
          </div>
        </div>

        {/* Data Analysis */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="text-indigo-600" size={24} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Analyze Pricing Data</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Click the <strong>Charts</strong> button on the dashboard to view:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li><strong>Price Distribution:</strong> See how listings are distributed across price ranges</li>
              <li><strong>Average Price by Year:</strong> Track how vehicle year affects pricing</li>
              <li><strong>Mileage vs Price:</strong> Understand the relationship between mileage and value</li>
              <li>Use these insights to set better target prices</li>
            </ul>
          </div>
        </div>

        {/* Favorites */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-pink-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">❤️</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900">Manage Favorites</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Keep track of interesting listings:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>Click the heart icon on any listing card to add it to favorites</li>
              <li>View your favorites count in the dashboard stats</li>
              <li>Use the favorite filter to see only your saved listings</li>
            </ul>
          </div>
        </div>

        {/* Logs */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span className="text-xl font-bold text-yellow-600">📄</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900">View Activity Logs</h2>
          </div>
          <div className="ml-13 space-y-3 text-gray-700">
            <p>Monitor scraping activity in the <strong>Logs</strong> page:</p>
            <ul className="list-disc ml-6 space-y-2">
              <li>See when scraping sessions start and stop</li>
              <li>Track how many listings were found in each session</li>
              <li>View errors or warnings that occurred</li>
              <li>Filter logs by level (info, success, warning, error)</li>
            </ul>
          </div>
        </div>

        {/* Tips */}
        <div className="bg-gradient-to-br from-green-500 to-teal-600 rounded-xl p-6 text-white shadow-lg">
          <h2 className="text-2xl font-bold mb-3">💡 Pro Tips</h2>
          <ul className="space-y-2 text-green-100">
            <li>• Create multiple searches for different vehicle types or price ranges</li>
            <li>• Set realistic target prices based on market data from the charts</li>
            <li>• Use shorter scraping intervals during peak hours for better deals</li>
            <li>• Enable browser notifications to never miss a great deal</li>
            <li>• Regularly check the logs to ensure scraping is working correctly</li>
            <li>• Favorite listings you're interested in to track them over time</li>
          </ul>
        </div>

        {/* Support */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-3">Need Help?</h2>
          <p className="text-gray-700">
            If you encounter any issues or have questions, please check the logs page for error details
            or contact support. Happy deal hunting!
          </p>
        </div>
      </div>
    </div>
  );
};

export default UserGuide;
