import React from 'react';
import ReactDOM from 'react-dom/client';

function App() {
  return (
    <div>
      <h1>jsx文件标题</h1>
      <p>React组件渲染成功啦啦啦</p>
        <a href="/test">访问测试页面</a>
    </div>
  );
}


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);





