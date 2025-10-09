import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_LOCALES, DELETE_LOCALE, type Locale } from '../graphql/locales';
import LocaleForm from './LocaleForm';

const LocaleManager: React.FC = () => {
  const [filter, setFilter] = useState<{
    language?: string;
    namespace?: string;
    isActive?: boolean;
  }>({});
  const [showForm, setShowForm] = useState(false);
  const [editingLocale, setEditingLocale] = useState<Locale | undefined>(undefined);

  const { data, loading, error, refetch } = useQuery(GET_LOCALES, {
    variables: { filter, skip: 0, limit: 100 },
    errorPolicy: 'all',
  });

  const [deleteLocale] = useMutation(DELETE_LOCALE, {
    onCompleted: () => {
      refetch();
    },
    onError: (error) => {
      console.error('Error deleting locale:', error);
    },
  });

  const locales: Locale[] = data?.locales || [];

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this locale?')) {
      try {
        await deleteLocale({ variables: { id } });
      } catch (err) {
        console.error('Error deleting locale:', err);
      }
    }
  };

  const handleFilterChange = (newFilter: typeof filter) => {
    setFilter(newFilter);
  };

  const handleCreateNew = () => {
    setEditingLocale(undefined);
    setShowForm(true);
  };

  const handleEdit = (locale: Locale) => {
    setEditingLocale(locale);
    setShowForm(true);
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditingLocale(undefined);
    refetch();
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingLocale(undefined);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return (
      <div style={{ color: 'red' }}>
        Error: {error.message}
        <button onClick={() => refetch()}>Retry</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Localization Management (GraphQL)</h1>
      
      {/* Filter Controls */}
      <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid #ddd', borderRadius: '4px' }}>
        <h3>Filters</h3>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <input
            type="text"
            placeholder="Language (e.g., en, ru)"
            value={filter.language || ''}
            onChange={(e) => handleFilterChange({ ...filter, language: e.target.value || undefined })}
            style={{ padding: '5px' }}
          />
          <input
            type="text"
            placeholder="Namespace"
            value={filter.namespace || ''}
            onChange={(e) => handleFilterChange({ ...filter, namespace: e.target.value || undefined })}
            style={{ padding: '5px' }}
          />
          <select
            value={filter.isActive === undefined ? '' : filter.isActive.toString()}
            onChange={(e) => {
              const value = e.target.value === '' ? undefined : e.target.value === 'true';
              handleFilterChange({ ...filter, isActive: value });
            }}
            style={{ padding: '5px' }}
          >
            <option value="">All</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
          <button onClick={() => setFilter({})}>Clear Filters</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button 
          onClick={handleCreateNew}
          style={{
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Create New Locale
        </button>
        <button onClick={() => refetch()}>Refresh</button>
      </div>
      
      <div style={{ marginTop: '20px' }}>
        <h2>Locales ({locales.length})</h2>
        {locales.length === 0 ? (
          <p>No locales found</p>
        ) : (
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>ID</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Key</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Value</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Language</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Namespace</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Active</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {locales.map((locale) => (
                <tr key={locale.id}>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{locale.id}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{locale.key}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{locale.value}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{locale.language}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>{locale.namespace}</td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    {locale.isActive ? '✅' : '❌'}
                  </td>
                  <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <button 
                        onClick={() => handleEdit(locale)}
                        style={{ 
                          backgroundColor: '#007bff', 
                          color: 'white', 
                          border: 'none', 
                          padding: '4px 8px', 
                          borderRadius: '3px',
                          cursor: 'pointer'
                        }}
                      >
                        Edit
                      </button>
                      <button 
                        onClick={() => handleDelete(locale.id)}
                        style={{ 
                          backgroundColor: '#ff4444', 
                          color: 'white', 
                          border: 'none', 
                          padding: '4px 8px', 
                          borderRadius: '3px',
                          cursor: 'pointer'
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showForm && (
        <LocaleForm
          locale={editingLocale}
          onSuccess={handleFormSuccess}
          onCancel={handleFormCancel}
        />
      )}
    </div>
  );
};

export default LocaleManager;
