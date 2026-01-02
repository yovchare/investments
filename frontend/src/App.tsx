import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Summary from './pages/Summary';
import Investments from './pages/Investments';
import RealEstate from './pages/RealEstate';
import Tickers from './pages/Tickers';
import Properties from './pages/Properties';
import Accounts from './pages/Accounts';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Summary />} />
            <Route path="/investments" element={<Investments />} />
            <Route path="/real-estate" element={<RealEstate />} />
            <Route path="/tickers" element={<Tickers />} />
            <Route path="/properties" element={<Properties />} />
            <Route path="/accounts" element={<Accounts />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
