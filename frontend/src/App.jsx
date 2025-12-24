import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import TransactionForm from './pages/TransactionForm';
import Budgets from './pages/Budgets';
import BudgetForm from './pages/BudgetForm';
import Reports from './pages/Reports';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/transactions"
            element={
              <ProtectedRoute>
                <Transactions />
              </ProtectedRoute>
            }
          />
          <Route
            path="/transactions/add"
            element={
              <ProtectedRoute>
                <TransactionForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/transactions/:id/edit"
            element={
              <ProtectedRoute>
                <TransactionForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/budgets"
            element={
              <ProtectedRoute>
                <Budgets />
              </ProtectedRoute>
            }
          />
          <Route
            path="/budgets/add"
            element={
              <ProtectedRoute>
                <BudgetForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/budgets/:id/edit"
            element={
              <ProtectedRoute>
                <BudgetForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

