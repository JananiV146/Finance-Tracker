import Transaction from '../models/Transaction.js';
import Budget from '../models/Budget.js';

// Transactions
export const listTransactions = async (userId) => {
  return await Transaction.find({ user_id: userId })
    .sort({ date: -1, _id: -1 })
    .lean();
};

export const insertTransaction = async (userId, date, type, amount, category, description = '') => {
  const tx = new Transaction({
    user_id: userId,
    date,
    type,
    amount: parseFloat(amount),
    category,
    description: description || '',
  });
  await tx.save();
  return tx._id.toString();
};

export const findTransaction = async (userId, txId) => {
  const tx = await Transaction.findOne({ _id: txId, user_id: userId }).lean();
  if (!tx) return null;
  return { ...tx, id: tx._id.toString() };
};

export const updateTransaction = async (userId, txId, fields) => {
  const result = await Transaction.updateOne(
    { _id: txId, user_id: userId },
    { $set: fields }
  );
  return result.matchedCount > 0;
};

export const deleteTransaction = async (userId, txId) => {
  const result = await Transaction.deleteOne({ _id: txId, user_id: userId });
  return result.deletedCount > 0;
};

export const totals = async (userId) => {
  const pipeline = [
    { $match: { user_id: userId } },
    { $group: { _id: '$type', total: { $sum: '$amount' } } },
  ];
  
  const results = await Transaction.aggregate(pipeline);
  const income = results.find(r => r._id === 'income')?.total || 0;
  const expense = results.find(r => r._id === 'expense')?.total || 0;
  
  return { income: parseFloat(income), expense: parseFloat(expense) };
};

export const recentTransactions = async (userId, limit = 10) => {
  const txs = await Transaction.find({ user_id: userId })
    .sort({ date: -1, _id: -1 })
    .limit(limit)
    .lean();
  return txs.map(tx => ({ ...tx, id: tx._id.toString() }));
};

export const spendByCategory = async (userId, month) => {
  const pipeline = [
    {
      $match: {
        user_id: userId,
        type: 'expense',
        date: { $regex: `^${month}` },
      },
    },
    { $group: { _id: '$category', spent: { $sum: '$amount' } } },
  ];
  
  const results = await Transaction.aggregate(pipeline);
  const spendMap = {};
  results.forEach(r => {
    spendMap[r._id] = parseFloat(r.spent);
  });
  return spendMap;
};

export const monthIncomeExpense = async (userId, months) => {
  const pipeline = [
    {
      $match: {
        user_id: userId,
        date: { $regex: `^(${months.join('|')})` },
      },
    },
    {
      $project: {
        m: { $substr: ['$date', 0, 7] },
        type: 1,
        amount: 1,
      },
    },
    {
      $group: {
        _id: { m: '$m', t: '$type' },
        total: { $sum: '$amount' },
      },
    },
  ];
  
  const results = await Transaction.aggregate(pipeline);
  const res = {};
  months.forEach(m => {
    res[m] = { income: 0.0, expense: 0.0 };
  });
  
  results.forEach(r => {
    const m = r._id.m;
    const t = r._id.t;
    if (res[m] && res[m][t] !== undefined) {
      res[m][t] = parseFloat(r.total);
    }
  });
  
  return res;
};

// Budgets
export const listBudgets = async (userId) => {
  const budgets = await Budget.find({ user_id: userId })
    .sort({ month: -1, category: 1 })
    .lean();
  return budgets.map(b => ({ ...b, id: b._id.toString() }));
};

export const addBudget = async (userId, month, amount, category) => {
  try {
    const budget = new Budget({
      user_id: userId,
      month,
      category: category || null,
      amount: parseFloat(amount),
    });
    await budget.save();
    return budget._id.toString();
  } catch (error) {
    if (error.code === 11000) {
      return null; // Duplicate
    }
    throw error;
  }
};

export const findBudget = async (userId, bid) => {
  const budget = await Budget.findOne({ _id: bid, user_id: userId }).lean();
  if (!budget) return null;
  return { ...budget, id: budget._id.toString() };
};

export const updateBudget = async (userId, bid, month, amount, category) => {
  try {
    const result = await Budget.updateOne(
      { _id: bid, user_id: userId },
      { $set: { month, category: category || null, amount: parseFloat(amount) } }
    );
    return result.matchedCount > 0;
  } catch (error) {
    if (error.code === 11000) {
      return false; // Duplicate
    }
    throw error;
  }
};

export const deleteBudget = async (userId, bid) => {
  const result = await Budget.deleteOne({ _id: bid, user_id: userId });
  return result.deletedCount > 0;
};

export const budgetsForMonth = async (userId, month) => {
  const budgets = await Budget.find({ user_id: userId, month })
    .sort({ category: 1 })
    .lean();
  return budgets.map(b => ({
    category: b.category,
    amount: parseFloat(b.amount),
  }));
};

