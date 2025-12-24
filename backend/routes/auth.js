import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { body, validationResult } from 'express-validator';
import User from '../models/User.js';
import { authMiddleware } from '../middleware/auth.js';

const router = express.Router();

const validatePassword = (password) => {
  if (password.length < 8) {
    return 'Password must be at least 8 characters long.';
  }
  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter.';
  }
  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter.';
  }
  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least one digit.';
  }
  if (!/[!@#$%^&*()\-_=+\[\]{};:'",.<>/?|`~]/.test(password)) {
    return 'Password must contain at least one special character.';
  }
  return null;
};

// Signup
router.post('/signup', [
  body('username').trim().notEmpty().withMessage('Username is required'),
  body('password').notEmpty().withMessage('Password is required'),
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    
    const { username, password, confirm } = req.body;
    
    if (password !== confirm) {
      return res.status(400).json({ message: 'Password and confirmation do not match.' });
    }
    
    const pwErr = validatePassword(password);
    if (pwErr) {
      return res.status(400).json({ message: pwErr });
    }
    
    const existing = await User.findOne({ username });
    if (existing) {
      return res.status(400).json({ message: 'This username is already taken. Please choose another one.' });
    }
    
    const password_hash = await bcrypt.hash(password, 10);
    const user = new User({ username, password_hash });
    await user.save();
    
    const token = jwt.sign(
      { userId: user._id },
      process.env.JWT_SECRET || 'dev-secret-change-me',
      { expiresIn: '7d' }
    );
    
    res.status(201).json({
      message: 'Account created! Welcome.',
      token,
      user: { id: user._id.toString(), username: user.username },
    });
  } catch (error) {
    if (error.code === 11000) {
      return res.status(400).json({ message: 'This username is already taken. Please choose another one.' });
    }
    res.status(500).json({ message: 'Server error' });
  }
});

// Login
router.post('/login', [
  body('username').trim().notEmpty(),
  body('password').notEmpty(),
], async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = await User.findOne({ username });
    
    if (!user || !(await bcrypt.compare(password, user.password_hash))) {
      return res.status(401).json({ message: 'Invalid username or password.' });
    }
    
    const token = jwt.sign(
      { userId: user._id },
      process.env.JWT_SECRET || 'dev-secret-change-me',
      { expiresIn: '7d' }
    );
    
    res.json({
      message: 'Logged in successfully.',
      token,
      user: { id: user._id.toString(), username: user.username },
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
});

// Get current user
router.get('/me', authMiddleware, async (req, res) => {
  res.json({ user: req.user });
});

// Logout (client-side token removal, but we can add token blacklist here if needed)
router.post('/logout', authMiddleware, (req, res) => {
  res.json({ message: 'Logged out.' });
});

export default router;

