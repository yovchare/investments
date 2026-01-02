import React from 'react';
import './PageLayout.css';

interface PageLayoutProps {
  title: string;
  children: React.ReactNode;
}

const PageLayout: React.FC<PageLayoutProps> = ({ title, children }) => {
  return (
    <div className="page-layout">
      <div className="page-header">
        <h1>{title}</h1>
      </div>
      <div className="page-content">
        {children}
      </div>
    </div>
  );
};

export default PageLayout;
