import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { HELLO_QUERY, GET_USERS, CREATE_USER, type User } from '../graphql/demo';

const Demo: React.FC = () => {
  const [newUserName, setNewUserName] = useState('');
  const [newUserEmail, setNewUserEmail] = useState('');

  const { data: helloData, loading: helloLoading } = useQuery(HELLO_QUERY);
  const { data: usersData, loading: usersLoading, refetch } = useQuery(GET_USERS);
  
  const [createUser] = useMutation(CREATE_USER, {
    onCompleted: () => {
      refetch();
      setNewUserName('');
      setNewUserEmail('');
    },
  });

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newUserName && newUserEmail) {
      await createUser({
        variables: {
          name: newUserName,
          email: newUserEmail,
        },
      });
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>GraphQL Demo</h2>
      
      {/* Hello Query */}
      <div style={{ marginBottom: '30px', padding: '15px', border: '1px solid #ddd', borderRadius: '5px' }}>
        <h3>Hello Query</h3>
        {helloLoading ? (
          <p>Loading...</p>
        ) : (
          <p><strong>Response:</strong> {helloData?.hello}</p>
        )}
      </div>

      {/* Users Query */}
      <div style={{ marginBottom: '30px', padding: '15px', border: '1px solid #ddd', borderRadius: '5px' }}>
        <h3>Users Query</h3>
        {usersLoading ? (
          <p>Loading...</p>
        ) : (
          <div>
            <p><strong>Users ({usersData?.users?.length || 0}):</strong></p>
            <ul>
              {usersData?.users?.map((user: User) => (
                <li key={user.id}>
                  {user.name} - {user.email}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Create User Mutation */}
      <div style={{ padding: '15px', border: '1px solid #ddd', borderRadius: '5px' }}>
        <h3>Create User Mutation</h3>
        <form onSubmit={handleCreateUser} style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <input
            type="text"
            placeholder="Name"
            value={newUserName}
            onChange={(e) => setNewUserName(e.target.value)}
            style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <input
            type="email"
            placeholder="Email"
            value={newUserEmail}
            onChange={(e) => setNewUserEmail(e.target.value)}
            style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <button
            type="submit"
            style={{
              padding: '8px 16px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Create User
          </button>
        </form>
      </div>
    </div>
  );
};

export default Demo;
