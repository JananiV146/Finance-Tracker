import express from 'express';
import { authMiddleware } from '../middleware/auth.js';
import { totals, recentTransactions, budgetsForMonth, spendByCategory } from '../utils/db.js';

const router = express.Router();
router.use(authMiddleware);

router.get('/', async (req, res) => {
  try {
    const userId = req.user.id;
    
    // Totals
    const t = await totals(userId);
    const income_total = t.income || 0.0;
    const expense_total = t.expense || 0.0;
    const balance = income_total - expense_total;
    
    // Recent transactions
    const recent = await recentTransactions(userId, 10);
    
    // Current month for budgets
    const today = new Date();
    const month = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    const budgets = await budgetsForMonth(userId, month);
    
    // Spend per category for month
    const spend_map = await spendByCategory(userId, month);
    
    res.json({
      balance,
      income_total,
      expense_total,
      recent,
      budgets,
      spend_map,
      month,
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;

