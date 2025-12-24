import jwt from 'jsonwebtoken';
import User from '../models/User.js';

export const authMiddleware = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
      return res.status(401).json({ message: 'No token provided' });
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'dev-secret-change-me');
    const user = await User.findById(decoded.userId).select('-password_hash').lean();
    
    if (!user) {
      return res.status(401).json({ message: 'User not found' });
    }
    
    req.user = { id: user._id.toString(), username: user.username };
    next();
  } catch (error) {
    return res.status(401).json({ message: 'Invalid token' });
  }
};

