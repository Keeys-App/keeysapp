import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Locale {
  id: number;
  key: string;
  value: string;
  language: string;
  namespace: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const LocaleManager: React.FC = () => {
  const [locales, setLocales] = useState<Locale[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLocales();
  }, []);

  const fetchLocales = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/v1/locales/`);
      setLocales(response.data);
      setError(null);
    } catch (err) {
      setError('Error loading locales');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return (
      <div style={{ color: 'red' }}>
        {error}
        <button onClick={fetchLocales}>Retry</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Localization Management</h1>
      <button onClick={fetchLocales}>Refresh</button>
      
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
                    {locale.is_active ? '✅' : '❌'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default LocaleManager;
