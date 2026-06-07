# Script-Server 中文文档

Script-Server 是一个功能完善的 Web 界面，用于执行脚本。通过这个平台，管理员可以配置现有的脚本，其他用户则可以通过友好的 Web 界面来执行这些脚本。

## 功能特性

- **多种脚本参数类型**：支持文本、标签、下拉选择、文件上传等多种参数类型
- **实时脚本输出**：实时显示脚本执行过程中的输出信息
- **用户输入交互**：用户可以在脚本执行过程中发送输入
- **身份认证**（可选）：支持 LDAP、Google OAuth、htpasswd 文件等认证方式
- **访问控制**：精细的权限管理
- **告警通知**：脚本执行状态的告警功能
- **日志记录和审计**：完整的执行日志和审计功能
- **格式化输出支持**：支持颜色、样式、光标定位、清屏等格式化输出
- **脚本输出文件下载**：支持下载脚本产生的输出文件
- **执行历史**：查看脚本执行历史记录
- **管理后台**：专门用于脚本配置的管理页面

## 技术栈

### 后端
- **语言**：Python 3.7+
- **Web 框架**：Tornado 5/6
- **主要模块**：
  - [main.py](file:///workspace/src/main.py) - 应用程序入口和初始化
  - [server.py](file:///workspace/src/web/server.py) - Web 服务器和路由处理
  - [execution_service.py](file:///workspace/src/execution/execution_service.py) - 脚本执行服务
  - [script_config.py](file:///workspace/src/model/script_config.py) - 脚本配置模型

### 前端
- **框架**：Vue.js
- **UI 库**：Materialize CSS
- **构建工具**：Vue CLI
- **主要文件**：
  - [MainApp.vue](file:///workspace/web-src/src/main-app/components/MainApp.vue) - 主应用组件
  - [AdminApp.vue](file:///workspace/web-src/src/admin/AdminApp.vue) - 管理后台组件

## 项目结构

```
/workspace/
├── src/                      # Python 后端源码
│   ├── auth/                 # 认证模块
│   ├── communications/       # 通信模块（告警等）
│   ├── execution/            # 执行服务
│   ├── features/             # 功能特性
│   ├── model/                # 数据模型
│   ├── web/                  # Web 服务
│   └── main.py               # 主入口文件
├── web/                      # 构建后的前端资源
├── web-src/                  # Vue.js 前端源码
│   ├── src/
│   │   ├── admin/            # 管理后台相关
│   │   ├── common/           # 公共组件
│   │   ├── main-app/         # 主应用
│   │   └── login/            # 登录页面
│   └── package.json
├── conf/                     # 配置目录
│   └── logging.json          # 日志配置
├── samples/                  # 示例配置和脚本
│   ├── configs/              # 脚本配置示例
│   ├── scripts/              # 示例脚本
│   └── themes/               # 主题示例
├── tools/                    # 工具脚本
│   ├── init.py               # 项目初始化脚本
│   └── build.py              # 构建脚本
├── launcher.py               # 服务启动脚本
└── requirements.txt          # Python 依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化项目

```bash
python tools/init.py --no-npm
```

这个脚本会下载预构建的 Web 资源文件。

### 3. 配置脚本

在 `conf/runners/` 目录下创建脚本配置文件。你可以参考 `samples/configs/` 目录下的示例配置。

### 4. 启动服务

```bash
python launcher.py
```

默认情况下，服务会在 http://localhost:5000 启动。

### 5. 访问界面

- **主界面**：http://localhost:5000
- **管理后台**：http://localhost:5000/admin.html

## 配置说明

### 服务端配置

服务端配置文件位于 `conf/conf.json`。主要配置项包括：

- 端口设置
- SSL 配置
- 认证配置
- 日志配置
- 告警配置

### 脚本配置

每个脚本都需要一个单独的 JSON 配置文件，包含以下信息：

- 脚本名称和描述
- 脚本路径和工作目录
- 参数定义（名称、类型、默认值、验证规则等）
- 访问控制
- 输出格式设置

## 主要功能模块

### 认证模块

位于 `src/auth/` 目录，支持多种认证方式：

- LDAP 认证
- Google OAuth
- GitLab OAuth
- htpasswd 文件认证
- Keycloak OpenID

### 执行服务

位于 `src/execution/` 目录，负责：

- 脚本的启动和管理
- 实时输出流处理
- 进程控制（停止、终止）
- 参数处理和验证

### Web 服务

位于 `src/web/` 目录，提供：

- RESTful API
- WebSocket 实时通信
- 静态文件服务
- 认证和授权处理

### 前端应用

主应用位于 `web-src/src/main-app/`，提供：

- 脚本列表展示
- 参数输入界面
- 执行输出展示
- 历史记录查看
- 定时任务管理

管理后台位于 `web-src/src/admin/`，提供：

- 脚本配置管理
- 历史记录查看
- 用户权限管理

## 开发指南

### 前端开发

```bash
cd web-src
npm install
npm run serve
```

### 后端开发

确保已安装 Python 依赖，然后直接运行：

```bash
python launcher.py
```

### 构建前端

```bash
cd web-src
npm run build
```

构建后的文件会输出到 `web/` 目录。

## 日志

- **服务日志**：`logs/server.log`
- **脚本执行日志**：`logs/processes/` 目录，文件格式为 `{脚本名称}_{客户端地址}_{日期}_{时间}.log`

## 安全说明

Script-Server 在设计上考虑了安全性，但建议：

1. 仅在受信任的网络环境中运行
2. 启用身份认证
3. 限制用户权限
4. 定期审查执行日志
5. 使用 HTTPS 加密传输

### 命令注入防护

Script-Server 保证所有用户参数作为参数传递给可执行脚本，不会被执行。但脚本本身应该注意正确处理用户输入，建议使用类型化参数以提高安全性。

### XSS 和 CSRF 防护

- 版本 1.17+ 已通过特殊令牌防护 XSRF 攻击
- XSS 防护遵循 OWASP 安全建议

## 贡献指南

如果你想为 Script-Server 做出贡献，可以：

1. 报告新功能建议或 Bug
2. 实现现有 Issue（包含前后端、简单/复杂的任务）
3. 帮助改进文档
4. 搭建演示服务器
5. 向同事、朋友、博客等推广项目

## 更多信息

- 项目主页：https://github.com/bugy/script-server
- 演示站点：https://script-server.net/
- 管理员界面截图：https://github.com/bugy/script-server/wiki/Admin-interface
- 脚本配置指南：https://github.com/bugy/script-server/wiki/Script-config
- 服务器配置指南：https://github.com/bugy/script-server/wiki/Server-configuration
