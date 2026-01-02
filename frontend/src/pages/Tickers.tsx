import React, { useState, useEffect } from 'react';
import PageLayout from '../components/PageLayout';
import { tickerService } from '../services';
import { Ticker, TickerCreate } from '../types';
import './Tickers.css';

const Tickers: React.FC = () => {
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newTickerSymbol, setNewTickerSymbol] = useState('');

  useEffect(() => {
    fetchTickers();
  }, []);

  const fetchTickers = async () => {
    try {
      setLoading(true);
      const response = await tickerService.getAll();
      setTickers(response.data);
      setError('');
    } catch (err: any) {
      console.error('Error fetching tickers:', err);
      if (err.code === 'ERR_NETWORK' || err.code === 'ECONNABORTED' || err.message === 'Network Error' || err.message === 'Request aborted') {
        setError('Cannot connect to backend server. Make sure it is running at http://localhost:8000');
      } else {
        setError('Failed to load tickers. Please try again.');
      }
      setTickers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTicker = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newTickerSymbol.trim()) {
      setError('Please enter a ticker symbol');
      return;
    }

    const tickerData: TickerCreate = {
      ticker_symbol: newTickerSymbol.toUpperCase(),
    };

    try {
      const response = await tickerService.create(tickerData);
      setTickers([...tickers, response.data].sort((a, b) => a.ticker_symbol.localeCompare(b.ticker_symbol)));
      setNewTickerSymbol('');
      setShowAddForm(false);
      setError('');
    } catch (err: any) {
      if (err.response?.data?.detail?.includes('already exists')) {
        setError('This ticker symbol has already been added');
      } else {
        setError('Failed to add ticker');
      }
      console.error('Error adding ticker:', err);
    }
  };

  const handleCancel = () => {
    setShowAddForm(false);
    setNewTickerSymbol('');
    setError('');
  };

  if (loading) {
    return (
      <PageLayout title="Tickers">
        <div className="loading">Loading tickers...</div>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Tickers">
      <div className="tickers-container">
        {error && (
          <div className="error-message">
            {error}
            {error.includes('Cannot connect') && (
              <div style={{ marginTop: '10px', fontSize: '14px' }}>
                <strong>To start the backend:</strong>
                <pre style={{ background: '#f5f5f5', padding: '8px', borderRadius: '4px', marginTop: '8px' }}>
                  cd backend{'\n'}
                  source venv/bin/activate{'\n'}
                  python3 -m app.main
                </pre>
              </div>
            )}
          </div>
        )}

        <div className="tickers-header">
          <button 
            className="btn-add" 
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? '✕ Cancel' : '+ Add Ticker'}
          </button>
        </div>

        {showAddForm && (
          <div className="add-ticker-form">
            <form onSubmit={handleAddTicker}>
              <div className="form-row-single">
                <div className="form-field">
                  <label>Ticker Symbol</label>
                  <input
                    type="text"
                    value={newTickerSymbol}
                    onChange={(e) => setNewTickerSymbol(e.target.value.toUpperCase())}
                    placeholder="e.g., AAPL, MSFT, GOOGL"
                    className="form-input"
                    autoFocus
                  />
                  <small className="form-help">Price data will be added later</small>
                </div>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-save">
                  Add Ticker
                </button>
                <button type="button" className="btn-cancel" onClick={handleCancel}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {tickers.length === 0 ? (
          <div className="empty-state">
            <p>No tickers yet. Click "Add Ticker" to add ticker symbols you want to track.</p>
          </div>
        ) : (
          <div className="ticker-list">
            <div className="ticker-grid">
              {tickers.map((ticker) => (
                <div key={ticker.ticker_id} className="ticker-card">
                  <span className="ticker-symbol">{ticker.ticker_symbol}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </PageLayout>
  );
};

export default Tickers;
