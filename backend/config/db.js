import mongoose from 'mongoose';

const connectDB = async () => {
  try {
    const uri = process.env.MONGODB_URI || 'mongodb+srv://jananivenkatachalam14:jananivenkatachalam@userauthentication.iagkujk.mongodb.net/?appName=userAuthentication';
    const dbName = process.env.MONGODB_DB || 'finance_tracker';
    
    await mongoose.connect(uri, {
      dbName: dbName,
      serverSelectionTimeoutMS: 5000,
    });
    
    console.log('MongoDB Connected to:', dbName);
    
    // Create indexes
    await ensureIndexes();
  } catch (error) {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  }
};

const ensureIndexes = async () => {
  const db = mongoose.connection.db;
  
  // Users indexes
  await db.collection('users').createIndex({ username: 1 }, { unique: true });
  
  // Transactions indexes
  await db.collection('transactions').createIndex({ user_id: 1, date: -1 });
  await db.collection('transactions').createIndex({ user_id: 1, type: 1 });
  await db.collection('transactions').createIndex({ user_id: 1, category: 1 });
  
  // Budgets unique index
  await db.collection('budgets').createIndex(
    { user_id: 1, month: 1, category: 1 },
    { unique: true }
  );
  
  console.log('Database indexes ensured');
};

export default connectDB;

