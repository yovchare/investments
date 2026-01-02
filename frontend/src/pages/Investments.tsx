import React from 'react';
import PageLayout from '../components/PageLayout';

const Investments: React.FC = () => {
  return (
    <PageLayout title="Investments">
      <div>
        <h2>Investment Holdings</h2>
        <p>This page will display your investment holdings across all accounts including:</p>
        <ul>
          <li>Current holdings by account</li>
          <li>Stock positions and values</li>
          <li>Ownership status (Owned, Unowned, Unvested)</li>
          <li>Historical performance</li>
          <li>Cost basis and gains/losses</li>
        </ul>
        <p style={{ marginTop: '20px', color: '#666', fontStyle: 'italic' }}>
          Content coming soon...
        </p>
      </div>
    </PageLayout>
  );
};

export default Investments;
