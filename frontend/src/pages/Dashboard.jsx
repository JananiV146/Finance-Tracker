import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await api.get('/dashboard');
      setData(res.data);
    } catch (err) {
      console.error('Failed to fetch dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) return null;

  const { balance, income_total, expense_total, recent, budgets, spend_map, month } = data;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-gray-800">Finance Tracker</h1>
              <div className="flex space-x-4">
                <Link to="/dashboard" className="text-blue-600 hover:text-blue-800">Dashboard</Link>
                <Link to="/transactions" className="text-gray-600 hover:text-gray-800">Transactions</Link>
                <Link to="/budgets" className="text-gray-600 hover:text-gray-800">Budgets</Link>
                <Link to="/reports" className="text-gray-600 hover:text-gray-800">Reports</Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user?.username}</span>
              <button
                onClick={logout}
                className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium mb-2">Balance</h3>
            <p className={`text-3xl font-bold ${balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${balance.toFixed(2)}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium mb-2">Total Income</h3>
            <p className="text-3xl font-bold text-green-600">${income_total.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm font-medium mb-2">Total Expenses</h3>
            <p className="text-3xl font-bold text-red-600">${expense_total.toFixed(2)}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800">Recent Transactions</h2>
              <Link to="/transactions" className="text-blue-600 hover:underline text-sm">
                View All
              </Link>
            </div>
            <div className="space-y-3">
              {recent.length === 0 ? (
                <p className="text-gray-500">No transactions yet</p>
              ) : (
                recent.map((tx) => (
                  <div key={tx.id} className="flex justify-between items-center border-b pb-2">
                    <div>
                      <p className="font-medium">{tx.category}</p>
                      <p className="text-sm text-gray-500">{tx.date}</p>
                    </div>
                    <p className={`font-bold ${tx.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                      {tx.type === 'income' ? '+' : '-'}${tx.amount.toFixed(2)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Budgets for {month}</h2>
            <div className="space-y-3">
              {budgets.length === 0 ? (
                <p className="text-gray-500">No budgets set for this month</p>
              ) : (
                budgets.map((budget, idx) => {
                  const spent = spend_map[budget.category || 'General'] || 0;
                  const percentage = (spent / budget.amount) * 100;
                  return (
                    <div key={idx} className="border-b pb-3">
                      <div className="flex justify-between mb-1">
                        <span className="font-medium">{budget.category || 'General'}</span>
                        <span className="text-sm text-gray-600">
                          ${spent.toFixed(2)} / ${budget.amount.toFixed(2)}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${percentage > 100 ? 'bg-red-600' : percentage > 80 ? 'bg-yellow-500' : 'bg-green-500'}`}
                          style={{ width: `${Math.min(percentage, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

