# Finance Tracker - MERN Stack

A full-stack finance tracking application built with MongoDB, Express.js, React, and Node.js. Features include transaction management, budgeting, and financial reports with beautiful charts.

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Chart.js
- **Backend**: Node.js, Express.js, MongoDB (Mongoose)
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: MongoDB Atlas

## Features

- 🔐 User authentication (Signup, Login, Logout)
- 💰 Transaction management (Income & Expenses)
- 📊 Budget tracking with monthly budgets
- 📈 Financial reports with interactive charts
- 🎨 Modern UI with Tailwind CSS
- 📱 Responsive design

## Project Structure

```
finance-tracker/
├── backend/          # Express.js API server
│   ├── config/       # Database configuration
│   ├── models/       # Mongoose models
│   ├── routes/       # API routes
│   ├── middleware/   # Auth middleware
│   ├── utils/        # Database utilities
│   └── server.js     # Entry point
├── frontend/         # React application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── context/     # React context
│   │   ├── utils/       # Utilities
│   │   └── App.jsx      # Main app component
│   └── package.json
└── README.md
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- MongoDB Atlas account (or local MongoDB)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the backend directory:
```env
PORT=5000
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB=finance_tracker
JWT_SECRET=your-secret-key-here
NODE_ENV=development
```

4. Start the backend server:
```bash
npm run dev
```

The API will be running on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the frontend directory (optional):
```env
VITE_API_URL=http://localhost:5000/api
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be running on `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Transactions
- `GET /api/transactions` - List all transactions
- `POST /api/transactions` - Create transaction
- `GET /api/transactions/:id` - Get transaction
- `PUT /api/transactions/:id` - Update transaction
- `DELETE /api/transactions/:id` - Delete transaction

### Budgets
- `GET /api/budgets` - List all budgets
- `POST /api/budgets` - Create budget
- `GET /api/budgets/:id` - Get budget
- `PUT /api/budgets/:id` - Update budget
- `DELETE /api/budgets/:id` - Delete budget

### Dashboard
- `GET /api/dashboard` - Get dashboard data

### Reports
- `GET /api/reports` - Get financial reports

## Password Requirements

- At least 8 characters
- At least one lowercase letter
- At least one uppercase letter
- At least one digit
- At least one special character

## Deployment

### Backend (Render/Railway/Heroku)

1. Set environment variables on your hosting platform
2. Update `MONGODB_URI` with your production MongoDB connection string
3. Deploy the backend folder

### Frontend (Vercel/Netlify)

1. Set `VITE_API_URL` to your backend API URL
2. Build the project: `npm run build`
3. Deploy the `dist` folder

## License

ISC
