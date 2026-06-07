# Script-Server 完整中文文档

## 📖 项目概述

**Script-Server** 是一个功能完善的 Web 界面，用于执行脚本。通过这个平台，管理员可以配置现有的脚本，其他用户则可以通过友好的 Web 界面来执行这些脚本。

**核心特点**：无需修改脚本代码，通过简单的 JSON 配置即可将命令行脚本转化为安全的 Web 应用，使非技术人员也能通过浏览器执行脚本任务。

### 🎯 项目定位

- **目标用户**：系统管理员、开发团队、运维人员、数据分析师
- **使用场景**：IT 运维自动化、数据分析处理、自动化测试、教育培训
- **技术门槛**：零代码基础即可使用，管理员需了解基本的 JSON 配置

---

## ✨ 核心功能详解

### 1️⃣ 脚本参数可视化

自动生成包含多种控件的 Web 表单，支持参数验证：

| 参数类型 | 说明 | 配置示例 |
|---------|------|---------|
| **text** | 文本输入框 | `{"name": "username", "type": "text"}` |
| **flag** | 开关/复选框 | `{"name": "debug", "type": "flag"}` |
| **select** | 下拉选择 | `{"name": "env", "type": "select", "values": ["dev", "prod"]}` |
| **file** | 文件上传 | `{"name": "input", "type": "file"}` |
| **password** | 密码输入 | `{"name": "token", "type": "password"}` |
| **date** | 日期选择器 | `{"name": "start_date", "type": "date"}` |
| **time** | 时间选择器 | `{"name": "scheduled_time", "type": "time"}` |
| **number** | 数字输入 | `{"name": "count", "type": "number"}` |

### 2️⃣ 实时交互能力

- **实时脚本输出**：WebSocket 实时推送，支持 ANSI 颜色、样式、光标定位、清屏等格式化输出
- **用户输入交互**：脚本执行过程中，用户可以动态发送输入数据
- **进程控制**：支持启动、停止、终止脚本进程

### 3️⃣ 权限与认证

支持多种认证方式，实现细粒度访问控制：

```json
{
  "auth": {
    "type": "ldap",
    "server": "ldap://ldap.example.com",
    "base_dn": "dc=example,dc=com"
  }
}
```

支持认证方式：
- ✅ LDAP 认证
- ✅ Google OAuth
- ✅ GitLab OAuth
- ✅ htpasswd 文件认证
- ✅ Keycloak OpenID
- ✅ Azure AD OAuth

### 4️⃣ 其他特色功能

- 🔔 **告警通知**：邮件、Webhook 等告警方式
- 📥 **输出文件下载**：支持下载脚本产生的文件
- 📜 **执行历史**：完整的执行记录和审计日志
- ⏰ **定时任务**：支持 cron 表达式配置定时执行
- 🎨 **主题定制**：支持自定义界面主题

---

## 🚀 快速开始

### 环境要求

**服务端**
- Python 3.5+ (推荐 3.7+)
- Tornado 4/5/6
- 支持系统：Linux（主要）、Windows、macOS

**客户端**
- 任意现代浏览器（Chrome、Firefox、Edge 等）
- 无需互联网连接，所有资源从服务器加载

### 安装步骤

#### 方式一：开发/测试环境

```bash
# 1. 克隆仓库
git clone https://github.com/bugy/script-server.git
cd script-server

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 初始化项目（下载 Web 资源）
python tools/init.py --no-npm

# 4. 复制示例配置
cp samples/conf.json conf/conf.json

# 5. 启动服务
python launcher.py
```

#### 方式二：Docker 部署（生产环境推荐）

```bash
# 创建数据目录
mkdir -p /data/script-server

# 下载并解压
wget https://github.com/bugy/script-server/releases/latest/download/script-server.zip
unzip script-server.zip -d /data/script-server

# 使用 docker-compose 启动
cd /data/script-server
docker-compose up -d
```

### 访问界面

服务启动后，访问以下地址：

| 界面 | 地址 |
|-----|------|
| 主界面 | http://localhost:5000 |
| 管理后台 | http://localhost:5000/admin.html |

---

## 📝 脚本配置详解

### 配置文件位置

所有脚本配置放在 `conf/runners/` 目录下，支持 JSON 和 YAML 格式。

### 基础配置示例

创建一个简单的 Hello World 脚本配置 `conf/runners/hello.json`：

```json
{
  "name": "Hello World",
  "script_path": "python scripts/hello.py",
  "description": "测试脚本示例",
  "working_directory": "/workspace",
  "parameters": [
    {
      "name": "name",
      "type": "text",
      "description": "你的名字",
      "default": "World",
      "required": true
    },
    {
      "name": "verbose",
      "type": "flag",
      "description": "显示详细信息",
      "default": false
    }
  ]
}
```

对应的 Python 脚本 `scripts/hello.py`：

```python
#!/usr/bin/env python3
import sys

name = sys.argv[1] if len(sys.argv) > 1 else "World"
verbose = "--verbose" in sys.argv or "-v" in sys.argv

if verbose:
    print(f"[DEBUG] 正在执行 Hello 脚本...")

print(f"Hello, {name}!")

if verbose:
    print(f"[DEBUG] 脚本执行完成")
```

### 参数高级配置

#### 带验证的文本输入

```json
{
  "name": "email",
  "type": "text",
  "description": "邮箱地址",
  "validation": {
    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
    "message": "请输入有效的邮箱地址"
  }
}
```

#### 带选项的下拉菜单

```json
{
  "name": "environment",
  "type": "select",
  "description": "运行环境",
  "values": ["development", "staging", "production"],
  "default": "development",
  "required": true
}
```

#### 文件上传配置

```json
{
  "name": "upload_file",
  "type": "file",
  "description": "上传 CSV 文件",
  "required": true,
  "validation": {
    "accept": ".csv",
    "max_size": 10485760
  }
}
```

### 访问控制配置

```json
{
  "allowed_users": ["admin", "developer1", "developer2"],
  "user_groups": ["developers", "admins"],
  "allowed_ips": ["192.168.1.*", "10.0.0.*"]
}
```

### 输出配置

```json
{
  "output_format": {
    "type": "ansi",
    "colors": true,
    "clear": true,
    "cursor": true
  },
  "output_files": ["result.csv", "report.pdf"],
  "requires_terminal": true
}
```

### 告警配置

```json
{
  "alerts": {
    "on_start": true,
    "on_success": false,
    "on_fail": true,
    "destinations": [
      {
        "type": "email",
        "recipients": ["admin@example.com"]
      },
      {
        "type": "http",
        "url": "https://hooks.example.com/webhook"
      }
    ]
  }
}
```

### 定时任务配置

```json
{
  "schedule": {
    "cron": "0 9 * * *",
    "timezone": "Asia/Shanghai",
    "enabled": true
  }
}
```

---

## 🎨 服务端配置

### 主配置文件

在 `conf/conf.json` 中配置：

```json
{
  "title": "Script Server",
  "port": 5000,
  "host": "0.0.0.0",
  
  "ssl": {
    "enabled": false,
    "key_path": "./ssl/key.pem",
    "cert_path": "./ssl/cert.pem"
  },
  
  "authentication": {
    "type": "ldap",
    "config": {}
  },
  
  "logging": {
    "level": "INFO",
    "folder": "logs"
  }
}
```

### 常用配置项

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| `title` | 网站标题 | "Script server" |
| `port` | 监听端口 | 5000 |
| `host` | 监听地址 | "0.0.0.0" |
| `ssl.enabled` | 启用 HTTPS | false |
| `logging.level` | 日志级别 | "INFO" |

---

## 💼 实际应用场景

### 场景一：IT 运维自动化

**需求**：为非技术人员提供服务器管理脚本的 Web 入口

**配置示例** - 日志清理脚本：

```json
{
  "name": "日志清理工具",
  "script_path": "/scripts/cleanup_logs.sh",
  "description": "清理服务器上的旧日志文件",
  "allowed_users": ["ops_team"],
  "parameters": [
    {
      "name": "days",
      "type": "number",
      "description": "保留最近几天的日志",
      "default": 7,
      "min": 1,
      "max": 365
    },
    {
      "name": "path",
      "type": "text",
      "description": "日志目录路径",
      "default": "/var/log",
      "required": true
    },
    {
      "name": "dry_run",
      "type": "flag",
      "description": "仅显示将删除的文件，不实际删除"
    }
  ],
  "alerts": {
    "on_success": true,
    "destinations": [{"type": "email", "recipients": ["ops@example.com"]}]
  }
}
```

### 场景二：数据分析处理

**需求**：分析师上传 CSV 文件，选择处理模式，获取分析结果

**配置示例** - 数据分析脚本：

```json
{
  "name": "销售数据分析",
  "script_path": "python /scripts/analyze_sales.py",
  "description": "分析销售数据并生成报告",
  "parameters": [
    {
      "name": "input_file",
      "type": "file",
      "description": "上传销售数据 CSV 文件",
      "required": true,
      "validation": {"accept": ".csv"}
    },
    {
      "name": "mode",
      "type": "select",
      "description": "分析模式",
      "values": ["summary", "detailed", "full"],
      "default": "summary"
    },
    {
      "name": "date_range",
      "type": "select",
      "description": "时间范围",
      "values": ["today", "week", "month", "year", "all"],
      "default": "month"
    }
  ],
  "output_files": [
    "analysis_report.csv",
    "charts.png"
  ]
}
```

### 场景三：自动化测试

**需求**：测试团队统一管理测试脚本，生成可复用测试套件

**配置示例** - API 集成测试：

```json
{
  "name": "API 集成测试",
  "script_path": "pytest /tests/api_tests.py -v",
  "description": "运行 API 集成测试套件",
  "allowed_users": ["qa_team"],
  "parameters": [
    {
      "name": "environment",
      "type": "select",
      "description": "测试环境",
      "values": ["dev", "staging", "prod"],
      "required": true
    },
    {
      "name": "test_suite",
      "type": "select",
      "description": "测试套件",
      "values": ["all", "smoke", "regression", "full"],
      "default": "smoke"
    },
    {
      "name": "parallel",
      "type": "flag",
      "description": "并行执行测试"
    },
    {
      "name": "generate_report",
      "type": "flag",
      "description": "生成 HTML 测试报告",
      "default": true
    }
  ],
  "output_format": {
    "type": "ansi",
    "colors": true
  },
  "output_files": [
    "test_report.html",
    "test_results.xml"
  ]
}
```

---

## 🔐 安全最佳实践

### 命令注入防护

Script-Server 保证所有用户参数作为参数传递给可执行脚本，**不会被执行**。

**防护措施**：

1. **使用类型化参数**：类型化参数会验证输入格式，更难被注入
   ```json
   {
     "name": "user_id",
     "type": "number",
     "validation": {"min": 1, "max": 999999}
   }
   ```

2. **参数加引号**：脚本中处理参数时使用双引号包裹
   ```bash
   # 正确写法
   python script.py "$param"
   
   # 错误写法（可能存在注入风险）
   python script.py $param
   ```

3. **参数白名单验证**：使用正则表达式限制输入
   ```json
   {
     "name": "username",
     "type": "text",
     "validation": {
       "pattern": "^[a-zA-Z0-9_]{3,20}$"
     }
   }
   ```

### XSS 和 CSRF 防护

- ✅ **版本 1.17+**：通过特殊令牌防护 XSRF 攻击
- ✅ **XSS 防护**：遵循 OWASP 安全建议
- ✅ **内容安全策略**：启用 CSP 头防止跨站脚本

### 生产环境安全建议

1. **启用 HTTPS**
   ```json
   {
     "ssl": {
       "enabled": true,
       "key_path": "/path/to/key.pem",
       "cert_path": "/path/to/cert.pem"
     }
   }
   ```

2. **启用身份认证**
   ```json
   {
     "authentication": {
       "type": "google",
       "client_id": "your-client-id",
       "allowed_domains": ["company.com"]
     }
   }
   ```

3. **限制访问**
   ```json
   {
     "allowed_ips": ["192.168.1.0/24"],
     "max_execution_time": 3600
   }
   ```

4. **定期审查日志**
   - 检查 `logs/server.log` 中的异常访问
   - 审查 `logs/processes/` 中的脚本执行记录

---

## 🐛 故障排查

### 常见问题

#### 问题 1：端口被占用

**错误信息**：
```
OSError: [Errno 98] Address already in use
```

**解决方案**：
1. 修改 `conf/conf.json` 中的端口
   ```json
   {
     "port": 8080
   }
   ```

2. 或者查找并停止占用端口的进程
   ```bash
   lsof -i :5000
   kill -9 <PID>
   ```

#### 问题 2：权限错误

**错误信息**：
```
Permission denied: '/path/to/script.sh'
```

**解决方案**：
```bash
# 检查脚本权限
ls -la /path/to/script.sh

# 添加执行权限
chmod +x /path/to/script.sh

# 检查目录权限
chmod 755 /path/to
```

#### 问题 3：Python 依赖缺失

**错误信息**：
```
ModuleNotFoundError: No module named 'tornado'
```

**解决方案**：
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或指定版本
pip install tornado==6.5.6
```

#### 问题 4：WebSocket 连接失败

**解决方案**：

1. 检查浏览器控制台是否有错误
2. 确认防火墙允许 WebSocket 连接
3. 检查反向代理配置（如使用 Nginx）

```nginx
location / {
    proxy_pass http://localhost:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

### 调试技巧

#### 启用详细日志

在 `conf/conf.json` 中配置：

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

#### 检查脚本执行

查看日志文件：

```bash
# 服务日志
tail -f logs/server.log

# 脚本执行日志
tail -f logs/processes/*

# 实时查看最新日志
tail -f logs/server.log | grep -i error
```

---

## 📊 日志说明

### 日志文件位置

| 类型 | 路径 | 说明 |
|-----|------|------|
| 服务日志 | `logs/server.log` | Web 服务器和业务日志 |
| 脚本日志 | `logs/processes/{脚本名}_{IP}_{日期}_{时间}.log` | 各脚本执行详情 |

### 日志级别

- **DEBUG**：详细调试信息
- **INFO**：一般信息
- **WARNING**：警告信息
- **ERROR**：错误信息

---

## 🛠️ 开发指南

### 项目结构

```
/workspace/
├── src/                      # Python 后端源码
│   ├── auth/                # 认证模块
│   │   ├── auth_google_oauth.py
│   │   ├── auth_ldap.py
│   │   ├── auth_htpasswd.py
│   │   └── ...
│   ├── communications/      # 通信模块
│   │   ├── alerts_service.py
│   │   └── ...
│   ├── execution/           # 执行服务
│   │   ├── execution_service.py
│   │   ├── executor.py
│   │   └── ...
│   ├── model/              # 数据模型
│   │   ├── script_config.py
│   │   ├── parameter_config.py
│   │   └── ...
│   ├── web/                # Web 服务
│   │   ├── server.py
│   │   ├── script_config_socket.py
│   │   └── ...
│   ├── scheduling/         # 定时任务
│   ├── features/          # 功能特性
│   └── main.py            # 入口文件
├── web/                    # 构建后的前端资源
├── web-src/                # Vue.js 前端源码
│   ├── src/
│   │   ├── admin/         # 管理后台
│   │   ├── common/        # 公共组件
│   │   ├── main-app/      # 主应用
│   │   └── login/         # 登录页面
│   └── package.json
├── conf/                   # 配置目录
│   ├── conf.json          # 主配置文件
│   ├── logging.json       # 日志配置
│   └── runners/           # 脚本配置
├── samples/               # 示例
│   ├── configs/           # 脚本配置示例
│   └── scripts/           # 示例脚本
├── tools/                 # 工具脚本
│   ├── init.py           # 初始化脚本
│   └── build.py          # 构建脚本
├── launcher.py            # 启动脚本
└── requirements.txt       # Python 依赖
```

### 前端开发

```bash
# 进入前端目录
cd web-src

# 安装依赖
npm install

# 开发模式（热重载）
npm run serve

# 构建生产版本
npm run build
```

### 后端开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 启动服务
python launcher.py

# 运行测试
pytest src/tests/
```

### 代码规范

**Python 代码规范**：
- 遵循 PEP 8
- 使用类型注解
- 添加文档字符串

**提交代码前**：
```bash
# 运行测试
pytest src/tests/

# 代码格式检查
black src/
isort src/
ruff check src/
```

---

## 📚 技术栈详情

### 后端技术栈

- **语言**：Python 3.5+（推荐 3.7+）
- **Web 框架**：Tornado 5/6（异步非阻塞）
- **主要依赖**：
  - tornado：Web 服务器
  - pyyaml：配置文件解析
  - cryptography：加密支持

### 前端技术栈

- **框架**：Vue.js 2.x
- **UI 库**：Materialize CSS
- **构建工具**：Vue CLI
- **状态管理**：Vuex
- **实时通信**：WebSocket（SockJS）

### 架构特点

1. **前后端分离**：RESTful API + WebSocket
2. **异步处理**：Tornado 异步框架，支持高并发
3. **实时交互**：WebSocket 推送，支持双向通信
4. **安全隔离**：参数传递而非命令拼接，防止注入

---

## 🤝 贡献指南

欢迎为 Script-Server 做出贡献！

### 如何贡献

1. **报告问题**：在 GitHub Issues 中提交 Bug 或功能建议
2. **实现功能**：查看现有 Issues，选择感兴趣的任务
3. **改进文档**：帮助完善项目文档
4. **测试项目**：编写和运行测试用例
5. **推广项目**：向朋友、同事介绍这个项目

### 开发流程

1. Fork 仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

### 代码规范

- 遵循现有代码风格
- 为新功能添加测试
- 更新相关文档
- 确保所有测试通过

---

## 📞 获取帮助

- 💬 **社区讨论**：https://gitter.im/script-server/community
- 🐛 **问题反馈**：https://github.com/bugy/script-server/issues
- 📧 **电子邮件**：buggygm@gmail.com
- 🌐 **官方网站**：https://github.com/bugy/script-server
- 🎮 **在线演示**：https://script-server.net/

---

## 📄 许可证

本项目采用 MIT 许可证。

---

**最后更新**：2026年6月7日
