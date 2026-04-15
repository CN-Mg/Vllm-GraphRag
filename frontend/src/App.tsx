import './App.css';
import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';
import ThemeWrapper from './context/ThemeWrapper';
import QuickStarter from './components/QuickStarter';
import ErrorBoundary from './components/UI/ErrroBoundary';

/* 前端应用的根组件，整合全局能力 */
// 入口组件，渲染 QuickStarter 组件
// 处理全局异常：通过 ErrorBoundary 捕获子组件报错，避免应用崩溃
const App: React.FC = () => {
  return (
    <>
      <ErrorBoundary>
        <ThemeWrapper>
          <QuickStarter />
        </ThemeWrapper>
      </ErrorBoundary>
    </>
  );
};

export default App;
