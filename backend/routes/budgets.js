import express from 'express';
import { body, validationResult } from 'express-validator';
import { authMiddleware } from '../middleware/auth.js';
import {
  listBudgets,
  addBudget,
  findBudget,
  updateBudget,
  deleteBudget,
} from '../utils/db.js';

const router = express.Router();
router.use(authMiddleware);

// List budgets
router.get('/', async (req, res) => {
  try {
    const budgets = await listBudgets(req.user.id);
    res.json(budgets);
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Add budget
router.post('/', [
  body('month').matches(/^\d{4}-\d{2}$/),
  body('amount').isFloat({ min: 0 }),
  body('category').optional(),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    
    const { month, amount, category } = req.body;
    const bid = await addBudget(req.user.id, month, amount, category || null);
    
    if (!bid) {
      return res.status(400).json({ message: 'Budget for this month/category already exists.' });
    }
    
    res.status(201).json({ message: 'Budget added.', id: bid });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Get budget
router.get('/:id', async (req, res) => {
  try {
    const budget = await findBudget(req.user.id, req.params.id);
    if (!budget) {
      return res.status(404).json({ message: 'Budget not found.' });
    }
    res.json(budget);
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Update budget
router.put('/:id', [
  body('month').matches(/^\d{4}-\d{2}$/),
  body('amount').isFloat({ min: 0 }),
  body('category').optional(),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    
    const budget = await findBudget(req.user.id, req.params.id);
    if (!budget) {
      return res.status(404).json({ message: 'Budget not found.' });
    }
    
    const { month, amount, category } = req.body;
    const updated = await updateBudget(req.user.id, req.params.id, month, amount, category || null);
    
    if (!updated) {
      return res.status(400).json({ message: 'A budget with this month/category already exists.' });
    }
    
    res.json({ message: 'Budget updated.' });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Delete budget
router.delete('/:id', async (req, res) => {
  try {
    const deleted = await deleteBudget(req.user.id, req.params.id);
    if (!deleted) {
      return res.status(404).json({ message: 'Budget not found.' });
    }
    res.json({ message: 'Budget deleted.' });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;

