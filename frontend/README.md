# LLM Graph Builder - Frontend

## 项目概述

LLM Graph Builder 是一个基于 React + TypeScript 构建的前端应用，专门为航空航天机械故障诊断领域设计。该应用提供直观的用户界面，支持非结构化数据上传、知识图谱可视化和智能对话交互，通过现代化的UI组件和流畅的用户体验，让复杂的知识图谱构建变得简单易用。

## 🎯 设计理念

本前端应用遵循以下设计原则：
- **组件化架构**：基于 React 18 的组件化开发，提高代码复用性和可维护性
- **类型安全**：使用 TypeScript 确保类型安全，减少运行时错误
- **响应式设计**：适配不同屏幕尺寸，提供一致的用户体验
- **状态管理**：使用 React Context API 进行全局状态管理
- **性能优化**：虚拟滚动、懒加载等技术确保应用性能

## 技术栈

### 核心框架
- **React 18.3.1** - 用户界面库
- **TypeScript 5.0.2** - 类型安全的 JavaScript 超集
- **Vite 4.5.3** - 快速的前端构建工具

### UI 组件库
- **Material-UI 5.15.10** - Material Design 风格的 React 组件库
- **Neo4j Design System** - Neo4j 官方设计系统组件
  - `@neo4j-ndl/base` - 基础组件
  - `@neo4j-ndl/react` - React 组件
  - `@neo4j-nvl/base` - Neo4j 可视化库基础
  - `@neo4j-nvl/react` - Neo4j 可视化 React 组件

### 样式框架
- **Tailwind CSS 3.4.1** - 实用优先的 CSS 框架
- **Emotion 11.11.0** - CSS-in-JS 库
- **PostCSS 8.4.33** - CSS 转换工具
- **Autoprefixer 10.4.17** - CSS 前缀自动添加

### 状态管理与路由
- **React Router 6.23.1** - 声明式路由
- **React Context API** - 全局状态管理

### 数据处理与网络
- **Axios 1.6.5** - HTTP 客户端
- **React Dropzone 14.2.3** - 文件拖拽上传

### 工具库
- **React Icons 5.2.1** - 图标库
- **UUID 9.0.1** - 唯一标识符生成
- **CLSX 2.1.1** - 条件 className 工具
- **React Markdown 9.0.1** - Markdown 渲染

### 开发工具
- **ESLint 8.45.0** - 代码质量检查
- **Prettier 2.7.1** - 代码格式化
- **ESLint Plugins** - React 相关插件

## 主要功能模块

### 1. 用户认证与连接管理
- **Neo4j 数据库连接**
  - 支持连接参数配置（URI、用户名、密码、数据库）
  - 连接状态实时监控
  - 连接信息本地持久化存储
- **Google OAuth 集成**
  - 使用 `@react-oauth/google` 实现 Google 登录

### 2. 文件管理
- **多源文件上传**
  - 本地文件拖拽上传
  - Web URL 扫描（支持网页、Wiki、GCS 等）
  - 支持多种文件格式：文档、图片、非结构化文本
- **文件列表管理**
  - 文件状态跟踪（New、Processing、Completed、Failed）
  - 文件选择与批量操作
  - 文件删除（可选择删除实体或仅文件）
  - 大文件处理提示（>5MB 自动提示）

### 3. 图谱生成与处理
- **LLM 模型选择**
  - 支持多种 LLM 模型：GLM、OpenAI GPT-4o、Ollama Qwen3
  - 模型配置动态切换
- **图谱配置**
  - 预定义 Schema 选择
  - 自定义 Schema 定义
  - 节点标签和关系类型配置
  - 多种图谱类型：Lexical Graph、Entity Graph、Knowledge Graph
- **文件处理流程**
  - 文件分块处理
  - 实时进度更新
  - 处理状态监控
  - 后端任务队列管理

### 4. 图谱可视化
- **Neo4j 集成**
  - 直接生成 Cypher 查询
  - 支持 Neo4j Bloom 链接生成
  - 可视化图谱预览
- **图谱视图**
  - 多种图谱展示模式
  - 节点和关系的样式配置
  - 图谱统计信息显示
  - 图谱缩放和拖拽

### 5. 智能聊天系统
- **多模式对话**
  - Vector 模式：基于向量相似度的问答
  - Graph 模式：基于图谱结构的问答
  - Graph+Vector 混合模式
  - Image+Graph+Vector 多模态模式
- **上下文管理**
  - 聊天历史持久化
  - 消息来源追踪
  - 会话状态管理
- **语音交互**
  - 文本转语音（TTS）
  - 语音合成控制

### 6. 系统增强功能
- **图谱增强**
  - 相似度图谱构建
  - 全文索引创建
  - 实体嵌入更新
- **孤立节点管理**
  - 孤立节点检测
  - 批量清理工具
- **任务监控**
  - 服务器状态实时更新
  - 大文件处理进度提示
  - 错误处理和重试机制

## 🏗️ 架构设计

### 组件层次结构
```
App (根组件)
├── ErrorBoundary (错误边界)
├── ThemeWrapper (主题包装)
│   └── QuickStarter (快速启动)
│       ├── PageLayout (主布局)
│       │   ├── Sidebar (侧边栏)
│       │   ├── MainContent (主内容区)
│       │   │   ├── DataSources (数据源)
│       │   │   │   ├── Local/DropZone (本地文件上传)
│       │   │   │   └── WebSources (Web URL导入)
│       │   │   ├── FileTable (文件列表)
│       │   │   ├── GraphView (图谱可视化)
│       │   │   └── ChatBot (聊天机器人)
│       │   └── Popups (弹窗组件)
│       └── DrawerChatbot (聊天抽屉)
└── ThemeProvider (主题提供者)
```

### 状态管理架构
```typescript
// Context 层级结构
ThemeWrapper (全局主题)
├── AlertContext (全局警告)
├── UserCredentialsContext (用户凭证)
├── UserMessagesContext (用户消息)
└── DataSourceContext (数据源状态)
```

### 核心模块实现

#### 1. 文件上传模块 (`src/components/DataSources/`)
```typescript
// Local/DropZone.tsx
interface DropZoneProps {
  onFileUpload: (files: File[]) => void;
  acceptedFormats: string[];
  maxSize: number;
}

const DropZone: React.FC<DropZoneProps> = ({ onFileUpload, acceptedFormats, maxSize }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    // 验证文件大小和格式
    const validFiles = acceptedFiles.filter(file => 
      file.size <= maxSize && acceptedFormats.includes(file.type)
    );
    onFileUpload(validFiles);
  }, [acceptedFormats, maxSize, onFileUpload]);
  
  // 使用 react-dropzone 实现拖拽上传
  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: acceptedFormats.join(','),
    maxSize: maxSize,
  });
}
```

#### 2. 图谱可视化模块 (`src/components/Graph/`)
```typescript
// GraphViewModal.tsx
interface GraphViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  cypherQuery: string;
  documentNames: string[];
}

const GraphViewModal: React.FC<GraphViewModalProps> = ({ 
  isOpen, 
  onClose, 
  cypherQuery,
  documentNames 
}) => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  
  // 获取图谱数据
  useEffect(() => {
    if (isOpen && cypherQuery) {
      fetchGraphData(cypherQuery).then(data => {
        setGraphData(data);
        setLoading(false);
      });
    }
  }, [isOpen, cypherQuery]);
  
  // 渲染图谱
  const renderGraph = () => {
    if (loading) return <Spinner />;
    if (!graphData) return <div>无数据</div>;
    
    return (
      <Neo4jGraph 
        data={graphData}
        options={graphOptions}
        onNodeClick={handleNodeClick}
        onRelationshipClick={handleRelationshipClick}
      />
    );
  };
}
```

#### 3. 智能对话模块 (`src/components/ChatBot/`)
```typescript
// ChatMessage.tsx
interface ChatMessageProps {
  message: ChatMessage;
  isUser: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser }) => {
  const [isTyping, setIsTyping] = useState(false);
  
  // 处理语音合成
  const handleSpeak = useCallback(() => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(message.content);
      speechSynthesis.speak(utterance);
    }
  }, [message.content]);
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        isUser 
          ? 'bg-blue-500 text-white' 
          : 'bg-gray-200 text-gray-800'
      }`}>
        <p>{message.content}</p>
        {!isUser && (
          <button 
            onClick={handleSpeak}
            className="mt-1 text-sm text-blue-500 hover:text-blue-700"
          >
            🔊 播放
          </button>
        )}
      </div>
    </div>
  );
};
```

#### 4. API 服务层 (`src/services/`)
```typescript
// ExtractAPI.ts
export class ExtractAPI {
  private baseURL: string;
  
  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  }
  
  async extractKnowledgeGraph(params: ExtractParams): Promise<ExtractResponse> {
    const response = await axios.post(`${this.baseURL}/extract`, params, {
      headers: {
        'Content-Type': 'application/json',
      },
      // 处理 SSE 流
      responseType: 'stream',
    });
    
    // 返回 EventSource 用于进度跟踪
    return {
      success: true,
      eventSource: response.data,
    };
  }
  
  // 监听处理进度
  listenToProcessingProgress(
    eventSource: EventSource,
    onProgress: (progress: ProcessingProgress) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ) {
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'progress') {
        onProgress(data.payload);
      } else if (data.type === 'complete') {
        onComplete();
        eventSource.close();
      } else if (data.type === 'error') {
        onError(new Error(data.payload));
        eventSource.close();
      }
    };
  }
}
```

## 项目结构

```
frontend/
├── public/                    # 静态资源
├── src/
│   ├── HOC/                  # 高阶组件
│   │   ├── CustomModal.tsx    # 自定义模态框包装器
│   │   └── SettingModalHOC.tsx # 设置模态框包装器
│   ├── components/            # 业务组件
│   │   ├── ChatBot/           # 聊天机器人相关
│   │   ├── DataSources/       # 数据源组件
│   │   │   └── Local/
│   │   │       └── DropZone.tsx # 本地文件拖拽
│   │   ├── Graph/             # 图谱相关组件
│   │   ├── Layout/            # 布局组件
│   │   ├── Popups/            # 弹窗组件
│   │   ├── UI/                # 通用 UI 组件
│   │   └── WebSources/        # Web 数据源组件
│   ├── context/               # React Context
│   │   ├── Alert.tsx          # 全局警告状态
│   │   ├── UserCredentials.tsx # 用户凭证管理
│   │   └── UserMessages.tsx   # 用户消息管理
│   ├── hooks/                 # 自定义 Hooks
│   │   ├── useSpeech.tsx      # 语音合成 Hook
│   │   └── useSse.tsx         # 服务器发送事件 Hook
│   ├── services/              # API 服务
│   │   ├── CommonAPI.ts       # 通用 API 调用
│   │   ├── ConnectAPI.ts      # 连接 API
│   │   ├── DeleteFiles.ts     # 删除文件 API
│   │   ├── ExtractAPI.ts      # 数据提取 API
│   │   ├── GetFiles.ts        # 获取文件列表
│   │   ├── GraphQuery.ts      # 图谱查询
│   │   ├── PostProcessing.ts  # 后处理 API
│   │   └── ...                # 其他 API 服务
│   ├── styling/               # 样式文件
│   ├── types.ts              # TypeScript 类型定义
│   ├── utils/                # 工具函数
│   ├── App.tsx               # 根组件
│   ├── index.css             # 全局样式
│   ├── index.tsx             # 应用入口
│   └── router.tsx            # 路由配置
├── package.json              # 依赖管理
├── tsconfig.json             # TypeScript 配置
├── vite.config.ts            # Vite 配置
├── tailwind.config.js        # Tailwind 配置
├── postcss.config.js         # PostCSS 配置
└── ...                       # 其他配置文件
```

## 核心组件说明

### App.tsx
- 应用的根组件
- 负责全局错误边界处理
- 整合主题包装器

### QuickStarter.tsx
- 应用启动组件
- 管理全局状态包装器
- 处理主题切换

### PageLayout.tsx
- 主布局组件
- 管理左右抽屉的展开/收起
- 协调各功能模块的显示

### Content.tsx
- 核心内容区域
- 处理文件列表显示
- 管理图谱生成流程
- 集成各种操作按钮

### FileTable
- 文件表格组件
- 显示文件状态和元数据
- 支持文件选择和批量操作

### DrawerChatbot
- 聊天机器人抽屉
- 显示聊天消息
- 支持发送新消息

## API 接口说明

### 主要 API 端点
- `POST /api/extract` - 文件提取
- `POST /api/upload` - 文件上传（分块）
- `POST /api/connect` - 数据库连接
- `POST /api/delete` - 删除文件
- `POST /api/query` - 图谱查询
- `POST /api/post-process` - 后处理
- `GET /api/status` - 状态查询
- `SSE /api/stream` - 服务器事件流

### API 请求格式
```typescript
// 通用 API 参数格式
interface APIParams {
  uri: string;
  userName: string;
  password: string;
  database: string;
}
```

## 🔧 开发指南与最佳实践

### 1. 组件开发规范

#### 组件结构
```typescript
// 标准组件模板
interface MyComponentProps {
  // 必需属性
  title: string;
  // 可选属性
  description?: string;
  // 回调函数
  onAction?: (data: DataType) => void;
  // 子组件
  children?: React.ReactNode;
}

const MyComponent: React.FC<MyComponentProps> = ({
  title,
  description,
  onAction,
  children
}) => {
  // 状态管理
  const [state, setState] = useState<StateType>(initialState);
  
  // 副作用
  useEffect(() => {
    // 副逻辑
  }, [dependency]);
  
  // 事件处理
  const handleClick = useCallback(() => {
    onAction?.(data);
  }, [onAction]);
  
  // 渲染
  return (
    <div className="my-component">
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      <button onClick={handleClick}>Action</button>
      {children}
    </div>
  );
};

export default MyComponent;
```

#### 样式约定
```typescript
// 使用 CLSX 进行条件样式
const buttonClasses = clsx(
  'base-button',
  'px-4 py-2 rounded-md',
  isLoading ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600',
  disabled && 'opacity-50 cursor-not-allowed'
);

// 使用 Tailwind CSS 实用类
const containerStyles = {
  maxWidth: '1200px',
  margin: '0 auto',
  padding: '1rem',
};

// 使用 Emotion 进行 CSS-in-JS
const styledDiv = styled.div`
  background: ${props => props.theme.primary};
  color: white;
  padding: 1rem;
  border-radius: 8px;
  
  @media (max-width: 768px) {
    padding: 0.5rem;
  }
`;
```

### 2. 状态管理最佳实践

#### Context 使用模式
```typescript
// 1. 创建 Context
export const UserContext = createContext<{
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
}>({
  user: null,
  login: () => {},
  logout: () => {},
});

// 2. 创建 Provider
export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  
  const login = useCallback((user: User) => {
    setUser(user);
    localStorage.setItem('user', JSON.stringify(user));
  }, []);
  
  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('user');
  }, []);
  
  return (
    <UserContext.Provider value={{ user, login, logout }}>
      {children}
    </UserContext.Provider>
  );
};

// 3. 在组件中使用
const UserProfile: React.FC = () => {
  const { user } = useContext(UserContext);
  
  if (!user) {
    return <div>Please login</div>;
  }
  
  return <div>Welcome, {user.name}</div>;
};
```

#### 自定义 Hooks
```typescript
// src/hooks/useApi.ts
export function useApi<T>(
  apiFunction: () => Promise<T>,
  deps: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiFunction();
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, deps);
  
  return { data, loading, error, execute };
}

// 使用示例
const { data: documents, loading, error } = useApi(
  () => GetFilesAPI.getUserDocuments(),
  [userId]
);
```

### 3. 错误处理策略

#### 全局错误边界
```typescript
// src/components/UI/ErrorBoundary.tsx
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // 可以发送到错误监控服务
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>出错了！</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            重试
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

### 4. 性能优化技巧

#### 组件懒加载
```typescript
// 使用 React.lazy 进行懒加载
const LazyGraphView = React.lazy(() => import('./Graph/GraphView'));

const App: React.FC = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyGraphView />
    </Suspense>
  );
};
```

#### 虚拟滚动实现
```typescript
// 对于大数据量的列表
interface VirtualListProps {
  items: any[];
  itemHeight: number;
  height: number;
}

const VirtualList: React.FC<VirtualListProps> = ({ items, itemHeight, height }) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(height / itemHeight) + 1,
    items.length
  );
  
  const visibleItems = items.slice(startIndex, endIndex);
  
  return (
    <div 
      style={{ height, overflowY: 'auto' }}
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: items.length * itemHeight }}>
        {visibleItems.map((item, index) => (
          <div 
            key={index}
            style={{ 
              position: 'absolute',
              top: (startIndex + index) * itemHeight,
              height: itemHeight 
            }}
          >
            {item.content}
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 5. 测试策略

#### 组件测试
```typescript
// 使用 Jest + React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

test('button renders correctly', () => {
  render(<Button onClick={mockClick}>Click me</Button>);
  
  const button = screen.getByRole('button', { name: /click me/i });
  expect(button).toBeInTheDocument();
});

test('button calls onClick when clicked', () => {
  const mockClick = jest.fn();
  render(<Button onClick={mockClick}>Click me</Button>);
  
  fireEvent.click(screen.getByRole('button'));
  expect(mockClick).toHaveBeenCalledTimes(1);
});
```

#### API 测试
```typescript
// 使用 MSW 模拟 API
import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.get('/api/documents', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: 1, name: 'Document 1' },
        { id: 2, name: 'Document 2' },
      ])
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('fetches documents', async () => {
  const { result } = renderHook(() => useApi(() => GetFilesAPI.getDocuments()));
  
  await act(async () => {
    await result.current.execute();
  });
  
  expect(result.current.data).toHaveLength(2);
});
```

## 开发指南

### 安装依赖
```bash
cd frontend
npm install
```

### 开发运行
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 代码检查
```bash
npm run lint
```

### 代码格式化
```bash
npm run format
```

## 🚀 部署与构建

### 环境变量配置

在 `.env` 文件中配置以下环境变量：

```env
# Neo4j 配置
BLOOM_URL=http://localhost:7474
VITE_NEO4J_URI=neo4j://localhost:7687
VITE_NEO4J_USERNAME=neo4j
VITE_NEO4J_PASSWORD=your_password

# 支持的数据源
REACT_APP_SOURCES=local,web

# 支持的 LLM 模型
LLM_MODELS=GLM,openai-gpt-4o,ollama_qwen3:8b

# 分块配置
CHUNK_SIZE=1048576
LARGE_FILE_SIZE=5242880
TIME_PER_PAGE=50

# 支持的聊天模式
CHAT_MODES=vector,graph,graph+vector,image+graph+vector

# API 配置
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# 缓存配置
VITE_CACHE_ENABLED=true
VITE_CACHE_TTL=3600000
```

### 构建命令

```bash
# 安装依赖
npm install

# 开发环境运行
npm run dev

# 生产环境构建
npm run build

# 构建分析
npm run build:analyze

# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 性能优化

### 1. 文件处理优化
- 大文件分块上传
- 并行处理多个文件
- 实时进度反馈

### 2. 渲染优化
- 组件懒加载
- 虚拟滚动（大数据量）
- 图谱渲染性能优化

### 3. 内存管理
- 及时清理未使用的资源
- 避免内存泄漏
- 优化状态管理
