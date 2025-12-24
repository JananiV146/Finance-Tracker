import mongoose from 'mongoose';

const transactionSchema = new mongoose.Schema({
  user_id: {
    type: String,
    required: true,
    index: true,
  },
  date: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    required: true,
    enum: ['income', 'expense'],
  },
  amount: {
    type: Number,
    required: true,
  },
  category: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
}, {
  timestamps: true,
});

export default mongoose.model('Transaction', transactionSchema);

