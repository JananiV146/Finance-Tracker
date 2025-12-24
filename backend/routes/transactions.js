import express from 'express';
import { body, validationResult } from 'express-validator';
import { authMiddleware } from '../middleware/auth.js';
import {
  listTransactions,
  insertTransaction,
  findTransaction,
  updateTransaction,
  deleteTransaction,
} from '../utils/db.js';

const router = express.Router();
router.use(authMiddleware);

// List transactions
router.get('/', async (req, res) => {
  try {
    const txs = await listTransactions(req.user.id);
    res.json(txs.map(tx => ({ ...tx, id: tx._id.toString() })));
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Add transaction
router.post('/', [
  body('date').optional().isISO8601(),
  body('type').isIn(['income', 'expense']),
  body('amount').isFloat({ min: 0 }),
  body('category').trim().notEmpty(),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    
    const { date, type, amount, category, description } = req.body;
    const dateStr = date || new Date().toISOString().split('T')[0];
    
    const txId = await insertTransaction(
      req.user.id,
      dateStr,
      type,
      amount,
      category,
      description || ''
    );
    
    res.status(201).json({ message: 'Transaction added.', id: txId });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Get transaction
router.get('/:id', async (req, res) => {
  try {
    const tx = await findTransaction(req.user.id, req.params.id);
    if (!tx) {
      return res.status(404).json({ message: 'Transaction not found.' });
    }
    res.json(tx);
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Update transaction
router.put('/:id', [
  body('date').optional().isISO8601(),
  body('type').optional().isIn(['income', 'expense']),
  body('amount').optional().isFloat({ min: 0 }),
  body('category').optional().trim().notEmpty(),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    
    const tx = await findTransaction(req.user.id, req.params.id);
    if (!tx) {
      return res.status(404).json({ message: 'Transaction not found.' });
    }
    
    const { date, type, amount, category, description } = req.body;
    const fields = {};
    if (date) fields.date = date;
    if (type) fields.type = type;
    if (amount !== undefined) fields.amount = parseFloat(amount);
    if (category) fields.category = category;
    if (description !== undefined) fields.description = description;
    
    await updateTransaction(req.user.id, req.params.id, fields);
    res.json({ message: 'Transaction updated.' });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Delete transaction
router.delete('/:id', async (req, res) => {
  try {
    const deleted = await deleteTransaction(req.user.id, req.params.id);
    if (!deleted) {
      return res.status(404).json({ message: 'Transaction not found.' });
    }
    res.json({ message: 'Transaction deleted.' });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;

