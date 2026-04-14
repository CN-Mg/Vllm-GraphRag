import ReactDOM from 'react-dom/client';
import './index.css';
import { RouterProvider } from 'react-router-dom';
import router from './router.tsx';

/* 前端应用的启动器，负责将 React 应用挂载到 DOM上，并提供路由功能 */
// 整个前端的 “入口闸门”，所有页面 / 组件最终通过这里渲染到浏览器页面
ReactDOM.createRoot(document.getElementById('root')!).render(<RouterProvider router={router}></RouterProvider>);
