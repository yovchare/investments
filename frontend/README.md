# Investment Tracker Frontend

React + TypeScript frontend for the Investment Tracker application.

## Features

- React 18 with TypeScript
- React Router for navigation
- Type-safe API client
- Responsive design
- Service layer for API interactions
- Modular page structure

## Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` to configure:
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000/api)

## Running the Application

Development mode:
```bash
npm start
```

The application will open at http://localhost:3000

Build for production:
```bash
npm run build
```

Run tests:
```bash
npm test
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx      # Original dashboard component
│   │   ├── Navigation.tsx     # Main navigation component
│   │   ├── Navigation.css     # Navigation styles
│   │   ├── PageLayout.tsx     # Reusable page layout component
│   │   └── PageLayout.css     # Page layout styles
│   ├── pages/
│   │   ├── Summary.tsx        # Portfolio summary page
│   │   ├── Investments.tsx    # Investment holdings page
│   │   ├── RealEstate.tsx     # Real estate page
│   │   ├── Tickers.tsx        # Stock tickers page
│   │   └── Accounts.tsx       # Account management page
│   ├── services/
│   │   ├── api.ts             # Axios client configuration
│   │   └── index.ts           # API service functions
│   ├── types/
│   │   └── index.ts           # TypeScript type definitions
│   ├── App.tsx                # Main application component with routing
│   ├── App.css                # Application styles
│   ├── index.tsx              # Application entry point
│   └── index.css              # Global styles
├── package.json
├── tsconfig.json
└── .env.example
```

## Development

### Using the API Services

The frontend includes type-safe service functions for all API endpoints:

```typescript
import { accountService, holdingService, propertyService } from './services';

// Get all accounts
const accounts = await accountService.getAll();

// Create a new account
const newAccount = await accountService.create({
  account_name: "Investment Account",
  description: "My main investment account"
});

// Update an account
await accountService.update(1, {
  description: "Updated description"
});

// Delete an account
await accountService.delete(1);
```

### Available Services

- `accountService` - Account CRUD operations
- `tickerService` - Ticker CRUD operations
- `holdingService` - Account holding CRUD operations
- `propertyService` - Property CRUD operations
- `propertyValueService` - Property value CRUD operations
- `propertyMortgageService` - Property mortgage CRUD operations
- `backupService` - Database backup and restore

### Adding New Components

1. Create component in `src/components/`
2. Import types from `src/types/`
3. Use service functions from `src/services/`
4. Add component to appropriate route or view

Example component:

```typescript
import React, { useEffect, useState } from 'react';
import { Account } from '../types';
import { accountService } from '../services';

const AccountList: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const response = await accountService.getAll();
        setAccounts(response.data);
      } catch (error) {
        console.error('Error fetching accounts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAccounts();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Accounts</h2>
      <ul>
        {accounts.map(account => (
          <li key={account.account_id}>
            {account.account_name} - {account.description}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AccountList;
```

## TypeScript Types

All API response and request types are defined in `src/types/index.ts`. These match the Pydantic models in the backend for full type safety.

## Styling

The application uses basic CSS for styling. You can enhance it by adding:
- CSS modules
- Styled-components
- Material-UI
- Tailwind CSS
- Or any other styling solution

## Environment Variables

- `REACT_APP_API_URL` - The base URL for the backend API

Note: Environment variables must be prefixed with `REACT_APP_` to be available in the React application.

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory. You can serve it with any static file server:

```bash
# Using serve
npx serve -s build

# Using Python
python -m http.server -d build 3000
```

## Dependencies

### Core
- **react**: UI library
- **react-dom**: React DOM renderer
- **typescript**: TypeScript compiler
- **react-scripts**: Create React App scripts

### API Client
- **axios**: HTTP client for API requests

### Development
- **@testing-library/react**: React testing utilities
- **@testing-library/jest-dom**: Custom Jest matchers
- **@testing-library/user-event**: User event simulation
