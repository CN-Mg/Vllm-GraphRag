import './App.css';
import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';
import ThemeWrapper from './context/ThemeWrapper';
import QuickStarter from './components/QuickStarter';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { APP_SOURCES } from './utils/Constants';
import ErrorBoundary from './components/UI/ErrroBoundary';

/* 前端应用的根组件，整合全局能力 */
// 入口组件，根据环境变量决定是否使用 OAuth 进行认证，并渲染 QuickStarter 组件
// 处理全局异常：通过 ErrorBoundary 捕获子组件报错，避免应用崩溃
const App: React.FC = () => {
  return (
    <>
      {APP_SOURCES != undefined && APP_SOURCES.includes('gcs') ? (
        <ErrorBoundary>
          <GoogleOAuthProvider clientId={process.env.GOOGLE_CLIENT_ID as string}>
            <ThemeWrapper>
              <QuickStarter />
            </ThemeWrapper>
          </GoogleOAuthProvider>
        </ErrorBoundary>
      ) : (
        <ErrorBoundary>
          <ThemeWrapper>
            <QuickStarter />
          </ThemeWrapper>
        </ErrorBoundary>
      )}
    </>
  );
};

export default App;
