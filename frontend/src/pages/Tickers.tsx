import React, { useState, useEffect } from 'react';
import PageLayout from '../components/PageLayout';
import { tickerService, tickerPriceService } from '../services';
import { Ticker, TickerCreate, TickerPrice } from '../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './Tickers.css';

interface TickerWithPrices extends Ticker {
  prices: TickerPrice[];
  pricesLoading: boolean;
}

const Tickers: React.FC = () => {
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [selectedTickerId, setSelectedTickerId] = useState<number | null>(null);
  const [selectedTickerData, setSelectedTickerData] = useState<TickerWithPrices | null>(null);
  const [loading, setLoading] = useState(true);
  const [pricesLoading, setPricesLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newTickerSymbol, setNewTickerSymbol] = useState('');

  useEffect(() => {
    fetchTickers();
  }, []);

  // Fetch prices when selected ticker changes
  useEffect(() => {
    if (!selectedTickerId) return;

    const fetchSelectedTickerPrices = async () => {
      setPricesLoading(true);
      try {
        const ticker = tickers.find(t => t.ticker_id === selectedTickerId);
        if (!ticker) return;

        console.log(`Fetching prices for ticker ${selectedTickerId} (${ticker.ticker_symbol})`);
        const pricesResponse = await tickerPriceService.getByTickerId(selectedTickerId);
        console.log(`Got ${pricesResponse.data.length} prices for ${ticker.ticker_symbol}`);

        setSelectedTickerData({
          ...ticker,
          prices: pricesResponse.data,
          pricesLoading: false,
        });
      } catch (err: any) {
        console.error(`Error fetching prices for ticker ${selectedTickerId}:`, err.response?.status, err.response?.data || err.message);
        const ticker = tickers.find(t => t.ticker_id === selectedTickerId);
        if (ticker) {
          setSelectedTickerData({
            ...ticker,
            prices: [],
            pricesLoading: false,
          });
        }
      } finally {
        setPricesLoading(false);
      }
    };

    fetchSelectedTickerPrices();
  }, [selectedTickerId, tickers]);

  const fetchTickers = async () => {
    try {
      setLoading(true);
      const response = await tickerService.getAll();
      
      setTickers(response.data);
      setError('');
      
      // Auto-select the first ticker
      if (response.data.length > 0) {
        setSelectedTickerId(response.data[0].ticker_id);
      }
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
          <div>
            {/* Ticker Grid */}
            <div className="ticker-grid">
              {tickers.map((ticker) => (
                <button
                  key={ticker.ticker_id}
                  className={`ticker-pill ${selectedTickerId === ticker.ticker_id ? 'active' : ''}`}
                  onClick={() => setSelectedTickerId(ticker.ticker_id)}
                >
                  {ticker.ticker_symbol}
                </button>
              ))}
            </div>

            {/* Selected Ticker Chart */}
            {selectedTickerData && (
              <div className="ticker-chart-container">
                <h2 className="ticker-chart-title">{selectedTickerData.ticker_symbol}</h2>
                
                {/* Performance Indicators */}
                {selectedTickerData.prices.length > 0 && (
                  <div className="performance-indicators">
                    {(() => {
                      const prices = selectedTickerData.prices;
                      const currentPrice = prices[prices.length - 1].price;
                      const currentDate = new Date(prices[prices.length - 1].date);
                      
                      const calculateChange = (daysAgo: number) => {
                        const targetDate = new Date(currentDate);
                        targetDate.setDate(targetDate.getDate() - daysAgo);
                        
                        // Find closest price to target date
                        let closestPrice = null;
                        let minDiff = Infinity;
                        
                        for (const p of prices) {
                          const priceDate = new Date(p.date);
                          const diff = Math.abs(targetDate.getTime() - priceDate.getTime());
                          if (diff < minDiff && priceDate <= currentDate) {
                            minDiff = diff;
                            closestPrice = p.price;
                          }
                        }
                        
                        if (closestPrice) {
                          return ((currentPrice - closestPrice) / closestPrice * 100).toFixed(2);
                        }
                        return null;
                      };
                      
                      const changes = [
                        { label: '1D', value: calculateChange(1) },
                        { label: '1W', value: calculateChange(7) },
                        { label: '1M', value: calculateChange(30) },
                        { label: '3M', value: calculateChange(90) },
                        { label: '1Y', value: calculateChange(365) },
                      ];
                      
                      return changes.map((change, idx) => (
                        <div key={idx} className="performance-indicator">
                          <span className="indicator-label">{change.label}</span>
                          {change.value !== null ? (
                            <span className={`indicator-value ${parseFloat(change.value) >= 0 ? 'positive' : 'negative'}`}>
                              {parseFloat(change.value) >= 0 ? '+' : ''}{change.value}%
                            </span>
                          ) : (
                            <span className="indicator-value">N/A</span>
                          )}
                        </div>
                      ));
                    })()}
                  </div>
                )}
                
                {pricesLoading ? (
                  <div className="chart-loading">Loading price data...</div>
                ) : selectedTickerData.prices.length === 0 ? (
                  <div className="chart-empty">No price data available</div>
                ) : (
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart
                      data={selectedTickerData.prices.map(p => ({
                        date: p.date,
                        price: p.price,
                        displayDate: new Date(p.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' }),
                      }))}
                      margin={{ top: 5, right: 30, left: 20, bottom: 80 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                      <XAxis 
                        dataKey="date" 
                        tick={{ fontSize: 12 }}
                        interval={Math.floor(selectedTickerData.prices.length / 10) || 0}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                        tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
                      />
                      <YAxis 
                        tick={{ fontSize: 12 }}
                        domain={['auto', 'auto']}
                        tickFormatter={(value) => `$${value.toFixed(2)}`}
                      />
                      <Tooltip 
                        formatter={(value: number | undefined) => {
                          if (value === undefined) return ['N/A', 'Price'];
                          return [`$${value.toFixed(2)}`, 'Price'];
                        }}
                        labelFormatter={(label) => {
                          return new Date(label).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                        }}
                        cursor={{ strokeDasharray: '3 3' }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="price" 
                        stroke="#2563eb" 
                        strokeWidth={2}
                        dot={{ r: 2, fill: "#2563eb" }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </PageLayout>
  );
};

export default Tickers;
