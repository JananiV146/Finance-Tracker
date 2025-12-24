import express from 'express';
import { authMiddleware } from '../middleware/auth.js';
import { monthIncomeExpense, spendByCategory } from '../utils/db.js';

const router = express.Router();
router.use(authMiddleware);

const monthSequence = (n) => {
  const today = new Date();
  const months = [];
  let y = today.getFullYear();
  let m = today.getMonth() + 1;
  
  for (let i = 0; i < n; i++) {
    months.push(`${y}-${String(m).padStart(2, '0')}`);
    m--;
    if (m === 0) {
      m = 12;
      y--;
    }
  }
  
  return months.reverse();
};

router.get('/', async (req, res) => {
  try {
    const userId = req.user.id;
    const months = monthSequence(6);
    
    // Income/Expense per month for last 6 months
    const month_ie = await monthIncomeExpense(userId, months);
    
    // Category breakdown for current month (expenses)
    const curr_month = months[months.length - 1];
    const spend_map = await spendByCategory(userId, curr_month);
    
    const cat_rows = Object.entries(spend_map)
      .map(([category, total]) => ({ category, total }))
      .sort((a, b) => b.total - a.total);
    
    res.json({
      months,
      month_income: months.map(m => month_ie[m]?.income || 0),
      month_expense: months.map(m => month_ie[m]?.expense || 0),
      categories: cat_rows.map(r => r.category),
      cat_totals: cat_rows.map(r => r.total),
      curr_month,
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;

