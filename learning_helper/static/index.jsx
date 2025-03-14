import React from 'react';
import ReactDOM from 'react-dom/client';

function App() {
  return (
    <div>
      <h1>Learning Helper</h1>
      <p>React组件渲染成功!</p>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
