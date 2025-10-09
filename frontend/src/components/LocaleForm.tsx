import React, { useState } from 'react';
import { useMutation } from '@apollo/client';
import { CREATE_LOCALE, UPDATE_LOCALE, type Locale, type LocaleCreateInput, type LocaleUpdateInput } from '../graphql/locales';

interface LocaleFormProps {
  locale?: Locale;
  onSuccess: () => void;
  onCancel: () => void;
}

const LocaleForm: React.FC<LocaleFormProps> = ({ locale, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    key: locale?.key || '',
    value: locale?.value || '',
    language: locale?.language || '',
    namespace: locale?.namespace || 'default',
    isActive: locale?.isActive ?? true,
  });

  const [createLocale] = useMutation(CREATE_LOCALE, {
    onCompleted: () => {
      onSuccess();
    },
    onError: (error) => {
      console.error('Error creating locale:', error);
      alert('Error creating locale: ' + error.message);
    },
  });

  const [updateLocale] = useMutation(UPDATE_LOCALE, {
    onCompleted: () => {
      onSuccess();
    },
    onError: (error) => {
      console.error('Error updating locale:', error);
      alert('Error updating locale: ' + error.message);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.key || !formData.value || !formData.language) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      if (locale) {
        // Update existing locale
        const updateInput: LocaleUpdateInput = {
          key: formData.key,
          value: formData.value,
          language: formData.language,
          namespace: formData.namespace,
          isActive: formData.isActive,
        };
        await updateLocale({
          variables: {
            id: locale.id,
            input: updateInput,
          },
        });
      } else {
        // Create new locale
        const createInput: LocaleCreateInput = {
          key: formData.key,
          value: formData.value,
          language: formData.language,
          namespace: formData.namespace,
          isActive: formData.isActive,
        };
        await createLocale({
          variables: {
            input: createInput,
          },
        });
      }
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      left: 0, 
      right: 0, 
      bottom: 0, 
      backgroundColor: 'rgba(0,0,0,0.5)', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{ 
        backgroundColor: 'white', 
        padding: '20px', 
        borderRadius: '8px', 
        width: '500px',
        maxHeight: '80vh',
        overflow: 'auto'
      }}>
        <h2>{locale ? 'Edit Locale' : 'Create New Locale'}</h2>
        
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Key *
            </label>
            <input
              type="text"
              name="key"
              value={formData.key}
              onChange={handleChange}
              required
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Value *
            </label>
            <textarea
              name="value"
              value={formData.value}
              onChange={handleChange}
              required
              rows={3}
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Language *
            </label>
            <input
              type="text"
              name="language"
              value={formData.language}
              onChange={handleChange}
              required
              placeholder="e.g., en, ru, es"
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Namespace
            </label>
            <input
              type="text"
              name="namespace"
              value={formData.namespace}
              onChange={handleChange}
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                name="isActive"
                checked={formData.isActive}
                onChange={handleChange}
              />
              <span style={{ fontWeight: 'bold' }}>Active</span>
            </label>
          </div>

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onCancel}
              style={{
                padding: '10px 20px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                backgroundColor: 'white',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '4px',
                backgroundColor: '#007bff',
                color: 'white',
                cursor: 'pointer'
              }}
            >
              {locale ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LocaleForm;
