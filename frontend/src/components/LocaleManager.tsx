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
      setError('Ошибка при загрузке локализаций');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (error) {
    return (
      <div style={{ color: 'red' }}>
        {error}
        <button onClick={fetchLocales}>Повторить</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Управление локализацией</h1>
      <button onClick={fetchLocales}>Обновить</button>
      
      <div style={{ marginTop: '20px' }}>
        <h2>Локализации ({locales.length})</h2>
        {locales.length === 0 ? (
          <p>Локализации не найдены</p>
        ) : (
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>ID</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Ключ</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Значение</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Язык</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Пространство</th>
                <th style={{ border: '1px solid #ddd', padding: '8px' }}>Активна</th>
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
