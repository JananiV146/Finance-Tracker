import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { user } = useAuth();

  if (user) {
    window.location.href = '/dashboard';
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
          Finance Tracker
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Track your income, expenses, and budgets with ease
        </p>
        <div className="space-y-4">
          <Link
            to="/login"
            className="block w-full bg-blue-600 text-white text-center py-3 rounded-lg hover:bg-blue-700 transition duration-200 font-semibold"
          >
            Login
          </Link>
          <Link
            to="/signup"
            className="block w-full bg-gray-200 text-gray-800 text-center py-3 rounded-lg hover:bg-gray-300 transition duration-200 font-semibold"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;

