import mongoose from 'mongoose';

const budgetSchema = new mongoose.Schema({
  user_id: {
    type: String,
    required: true,
    index: true,
  },
  month: {
    type: String,
    required: true,
  },
  category: {
    type: String,
    default: null,
  },
  amount: {
    type: Number,
    required: true,
  },
}, {
  timestamps: true,
});

budgetSchema.index({ user_id: 1, month: 1, category: 1 }, { unique: true });

export default mongoose.model('Budget', budgetSchema);

