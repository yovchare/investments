import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Summary' },
    { path: '/investments', label: 'Investments' },
    { path: '/real-estate', label: 'Real Estate' },
    { path: '/tickers', label: 'Tickers' },
    { path: '/properties', label: 'Properties' },
    { path: '/accounts', label: 'Accounts' },
  ];

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <h2>Investment Tracker</h2>
      </div>
      <ul className="nav-menu">
        {navItems.map((item) => (
          <li key={item.path} className="nav-item">
            <Link
              to={item.path}
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Navigation;
