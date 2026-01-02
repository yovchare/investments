import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div>
      <h1>Investment Tracker Dashboard</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '20px' }}>
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h2>Accounts</h2>
          <p>Manage your investment accounts</p>
        </div>
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h2>Holdings</h2>
          <p>Track your stock holdings</p>
        </div>
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h2>Properties</h2>
          <p>Monitor real estate investments</p>
        </div>
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h2>Analytics</h2>
          <p>View portfolio analytics</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
