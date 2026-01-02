import React from 'react';
import PageLayout from '../components/PageLayout';

const Summary: React.FC = () => {
  return (
    <PageLayout title="Summary">
      <div>
        <h2>Portfolio Overview</h2>
        <p>Welcome to your Investment Tracker. This page will display a comprehensive summary of your portfolio including:</p>
        <ul>
          <li>Total net worth</li>
          <li>Investment account balances</li>
          <li>Real estate equity</li>
          <li>Performance charts</li>
          <li>Asset allocation</li>
        </ul>
        <p style={{ marginTop: '20px', color: '#666', fontStyle: 'italic' }}>
          Content coming soon...
        </p>
      </div>
    </PageLayout>
  );
};

export default Summary;
