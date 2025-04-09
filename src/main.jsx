import React from 'react'
import ReactDOM from 'react-dom/client'
import ChatApplication from './ChatApplication'

// Simple app without authentication
const App = () => {
  return <ChatApplication />;
};

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)