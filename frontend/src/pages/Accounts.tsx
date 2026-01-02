import React, { useState, useEffect } from 'react';
import PageLayout from '../components/PageLayout';
import { accountService } from '../services';
import { Account, AccountCreate } from '../types';
import './Accounts.css';

const Accounts: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [newlyCreatedId, setNewlyCreatedId] = useState<number | null>(null);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const response = await accountService.getAll();
      setAccounts(response.data);
      setError('');
    } catch (err: any) {
      console.error('Error fetching accounts:', err);
      if (err.code === 'ERR_NETWORK' || err.code === 'ECONNABORTED' || err.message === 'Network Error' || err.message === 'Request aborted') {
        setError('Cannot connect to backend server. Make sure it is running at http://localhost:8000');
      } else {
        setError('Failed to load accounts. Please try again.');
      }
      // Set empty accounts on error so we show empty state instead of loading forever
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = async () => {
    const newAccount: AccountCreate = {
      account_name: 'New Account',
      description: '',
    };

    try {
      const response = await accountService.create(newAccount);
      setAccounts([...accounts, response.data]);
      // Mark as newly created and automatically start editing
      setNewlyCreatedId(response.data.account_id);
      setEditingId(response.data.account_id);
      setEditName(response.data.account_name);
      setEditDescription(response.data.description || '');
    } catch (err) {
      setError('Failed to create account');
      console.error('Error creating account:', err);
    }
  };

  const handleEdit = (account: Account) => {
    setEditingId(account.account_id);
    setEditName(account.account_name);
    setEditDescription(account.description || '');
  };

  const handleSave = async (accountId: number) => {
    try {
      const response = await accountService.update(accountId, {
        account_name: editName,
        description: editDescription,
      });
      setAccounts(accounts.map(acc => 
        acc.account_id === accountId ? response.data : acc
      ));
      setEditingId(null);
      setNewlyCreatedId(null); // Clear newly created flag after successful save
      setError('');
    } catch (err) {
      setError('Failed to update account');
      console.error('Error updating account:', err);
    }
  };

  const handleCancel = async () => {
    // If canceling a newly created account that hasn't been saved, delete it
    if (newlyCreatedId !== null && editingId === newlyCreatedId) {
      try {
        await accountService.delete(newlyCreatedId);
        setAccounts(accounts.filter(acc => acc.account_id !== newlyCreatedId));
      } catch (err) {
        console.error('Error deleting unsaved account:', err);
      }
      setNewlyCreatedId(null);
    }
    setEditingId(null);
    setEditName('');
    setEditDescription('');
  };

  const handleDelete = async (accountId: number) => {
    if (!window.confirm('Are you sure you want to delete this account?')) {
      return;
    }

    try {
      await accountService.delete(accountId);
      setAccounts(accounts.filter(acc => acc.account_id !== accountId));
      setError('');
    } catch (err) {
      setError('Failed to delete account');
      console.error('Error deleting account:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent, accountId: number) => {
    if (e.key === 'Enter') {
      handleSave(accountId);
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (loading) {
    return (
      <PageLayout title="Accounts">
        <div className="loading">Loading accounts...</div>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Accounts">
      <div className="accounts-container">
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

        <div className="accounts-header">
          <button className="btn-add" onClick={handleAddAccount}>
            + Add Account
          </button>
        </div>

        {accounts.length === 0 ? (
          <div className="empty-state">
            <p>No accounts yet. Click "Add Account" to create your first account.</p>
          </div>
        ) : (
          <div className="accounts-table">
            {accounts.map((account) => (
              <div key={account.account_id} className="account-row">
                {editingId === account.account_id ? (
                  <div className="account-edit-mode">
                    <div className="edit-field">
                      <label>Account Name</label>
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        onKeyDown={(e) => handleKeyPress(e, account.account_id)}
                        autoFocus
                        className="edit-input"
                      />
                    </div>
                    <div className="edit-field">
                      <label>Description</label>
                      <input
                        type="text"
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        onKeyDown={(e) => handleKeyPress(e, account.account_id)}
                        className="edit-input"
                      />
                    </div>
                    <div className="edit-actions">
                      <button 
                        className="btn-save" 
                        onClick={() => handleSave(account.account_id)}
                      >
                        Save
                      </button>
                      <button 
                        className="btn-cancel" 
                        onClick={handleCancel}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="account-info">
                      <div className="account-name">{account.account_name}</div>
                      <div className="account-description">
                        {account.description || <span className="no-description">No description</span>}
                      </div>
                    </div>
                    <div className="account-actions">
                      <button
                        className="btn-icon btn-edit"
                        onClick={() => handleEdit(account)}
                        title="Edit account"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-icon btn-delete"
                        onClick={() => handleDelete(account.account_id)}
                        title="Delete account"
                      >
                        🗑️
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  );
};

export default Accounts;
