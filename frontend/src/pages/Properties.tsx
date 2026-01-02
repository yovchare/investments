import React, { useState, useEffect } from 'react';
import PageLayout from '../components/PageLayout';
import { propertyService } from '../services';
import { Property, PropertyCreate } from '../types';
import './Properties.css';

const Properties: React.FC = () => {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState('');
  const [newlyCreatedId, setNewlyCreatedId] = useState<number | null>(null);

  useEffect(() => {
    fetchProperties();
  }, []);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      const response = await propertyService.getAll();
      setProperties(response.data);
      setError('');
    } catch (err: any) {
      console.error('Error fetching properties:', err);
      if (err.code === 'ERR_NETWORK' || err.code === 'ECONNABORTED' || err.message === 'Network Error' || err.message === 'Request aborted') {
        setError('Cannot connect to backend server. Make sure it is running at http://localhost:8000');
      } else {
        setError('Failed to load properties. Please try again.');
      }
      setProperties([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddProperty = async () => {
    const newProperty: PropertyCreate = {
      name: 'New Property',
    };

    try {
      const response = await propertyService.create(newProperty);
      setProperties([...properties, response.data]);
      // Mark as newly created and automatically start editing
      setNewlyCreatedId(response.data.property_id);
      setEditingId(response.data.property_id);
      setEditName(response.data.name);
    } catch (err) {
      setError('Failed to create property');
      console.error('Error creating property:', err);
    }
  };

  const handleEdit = (property: Property) => {
    setEditingId(property.property_id);
    setEditName(property.name);
  };

  const handleSave = async (propertyId: number) => {
    try {
      const response = await propertyService.update(propertyId, {
        name: editName,
      });
      setProperties(properties.map(prop => 
        prop.property_id === propertyId ? response.data : prop
      ));
      setEditingId(null);
      setNewlyCreatedId(null); // Clear newly created flag after successful save
      setError('');
    } catch (err) {
      setError('Failed to update property');
      console.error('Error updating property:', err);
    }
  };

  const handleCancel = async () => {
    // If canceling a newly created property that hasn't been saved, delete it
    if (newlyCreatedId !== null && editingId === newlyCreatedId) {
      try {
        await propertyService.delete(newlyCreatedId);
        setProperties(properties.filter(prop => prop.property_id !== newlyCreatedId));
      } catch (err) {
        console.error('Error deleting unsaved property:', err);
      }
      setNewlyCreatedId(null);
    }
    setEditingId(null);
    setEditName('');
  };

  const handleDelete = async (propertyId: number) => {
    if (!window.confirm('Are you sure you want to delete this property?')) {
      return;
    }

    try {
      await propertyService.delete(propertyId);
      setProperties(properties.filter(prop => prop.property_id !== propertyId));
      setError('');
    } catch (err) {
      setError('Failed to delete property');
      console.error('Error deleting property:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent, propertyId: number) => {
    if (e.key === 'Enter') {
      handleSave(propertyId);
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  if (loading) {
    return (
      <PageLayout title="Properties">
        <div className="loading">Loading properties...</div>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Properties">
      <div className="properties-container">
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

        <div className="properties-header">
          <button className="btn-add" onClick={handleAddProperty}>
            + Add Property
          </button>
        </div>

        {properties.length === 0 ? (
          <div className="empty-state">
            <p>No properties yet. Click "Add Property" to create your first property.</p>
          </div>
        ) : (
          <div className="properties-table">
            {properties.map((property) => (
              <div key={property.property_id} className="property-row">
                {editingId === property.property_id ? (
                  <div className="property-edit-mode">
                    <div className="edit-field">
                      <label>Property Name</label>
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        onKeyDown={(e) => handleKeyPress(e, property.property_id)}
                        autoFocus
                        className="edit-input"
                      />
                    </div>
                    <div className="edit-actions">
                      <button 
                        className="btn-save" 
                        onClick={() => handleSave(property.property_id)}
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
                    <div className="property-info">
                      <div className="property-name">{property.name}</div>
                    </div>
                    <div className="property-actions">
                      <button
                        className="btn-icon btn-edit"
                        onClick={() => handleEdit(property)}
                        title="Edit property"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-icon btn-delete"
                        onClick={() => handleDelete(property.property_id)}
                        title="Delete property"
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

export default Properties;
