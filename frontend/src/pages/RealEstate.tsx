import React from 'react';
import PageLayout from '../components/PageLayout';

const RealEstate: React.FC = () => {
  return (
    <PageLayout title="Real Estate">
      <div>
        <h2>Real Estate Portfolio</h2>
        <p>This page will display your real estate investments including:</p>
        <ul>
          <li>Property listings and details</li>
          <li>Current valuations</li>
          <li>Outstanding mortgages</li>
          <li>Equity calculations</li>
          <li>Value trends over time</li>
        </ul>
        <p style={{ marginTop: '20px', color: '#666', fontStyle: 'italic' }}>
          Content coming soon...
        </p>
      </div>
    </PageLayout>
  );
};

export default RealEstate;
