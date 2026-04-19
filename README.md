# 一点天惊 - 智能点名程序 Android版本

基于Kivy框架开发的Android点名器应用，复刻原版桌面版的所有功能和界面效果。

## 功能特点

### 1. 加载界面
- 复刻原版的加载动画效果
- 中央"点"字大字显示
- 进度条动画
- 边角装饰图案

### 2. 导入文件界面（新增多种导入方式）
- **方法一**: 从Excel文件导入 (.xlsx/.xls)
- **方法二**: 从CSV文件导入
- **方法三**: 从文本文件导入 (.txt)
- **方法四**: 粘贴文本导入（支持逗号、空格、换行分隔）
- **方法五**: 从已有点名器导入

### 3. 手动输入界面
- 逐个人名输入
- 实时查看已添加列表
- 支持删除已添加的人名
- 空数据返回提示

### 4. 爆率修改界面
- 显示所有人名列表
- 调整每个人名的出现次数
- 增加/减少按钮
- 直接输入数字修改
- 可重复点名选项
- 恢复默认设置

### 5. 点名界面（与原版一模一样）
- 完全复刻原版的视觉效果
- 深色主题背景 (#1a1a2e)
- 星星闪烁动画装饰
- 边角彩色装饰线
- 中央名字显示区域
- 名字滚动动画效果
- 粒子爆炸特效
- 绿色闪烁效果
- 支持点击屏幕快速点名
- 名单查看功能
- 全屏模式

### 6. 已有点名器列表
- 显示所有已创建的点名器
- 显示人数统计
- 显示可重复/不可重复状态
- 运行、编辑、删除操作

## 技术栈

- **Python 3.8+**
- **Kivy 2.2.1** - 跨平台GUI框架
- **openpyxl** - Excel文件处理
- **xlrd** - 旧版Excel文件支持

## 项目结构

```
rollcall_android/
├── main.py                 # 主入口文件
├── buildozer.spec         # Android打包配置
├── requirements.txt       # Python依赖
├── README.md             # 项目说明
└── screens/              # 界面模块
    ├── __init__.py
    ├── import_screen.py   # 导入文件界面
    ├── input_screen.py    # 手动输入界面
    ├── rate_screen.py     # 爆率修改界面
    ├── name_screen.py     # 命名界面
    ├── list_screen.py     # 已有点名器列表
    ├── rollcall_screen.py # 点名界面
    └── about_screen.py    # 关于界面
```

## 开发环境搭建

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 运行开发版本

```bash
python main.py
```

## 打包APK

### 方法一：使用Buildozer（推荐）

#### Linux/macOS

1. 安装Buildozer依赖
```bash
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

2. 安装Buildozer
```bash
pip install buildozer
```

3. 安装Android SDK和NDK
```bash
buildozer android debug deploy run
```

第一次运行会自动下载所需的SDK和NDK。

#### Windows

Windows不支持直接运行Buildozer，建议使用：
- **WSL (Windows Subsystem for Linux)**
- **Docker**
- **虚拟机**

### 方法二：使用Docker

```bash
docker run --rm -v "$(pwd)":/home/user/app kivy/buildozer android debug
```

### 方法三：使用Google Colab

可以使用Google Colab免费打包APK：

```python
# 在Colab中运行
!pip install buildozer
!buildozer android debug
```

## 打包步骤

1. 确保项目文件完整
2. 修改 `buildozer.spec` 中的配置（如需要）
3. 运行打包命令：

```bash
buildozer android debug
```

4. 生成的APK文件位于：
   - `bin/rollcall-6.0.0.0-arm64-v8a_armeabi-v7a-debug.apk`

## 发布版本打包

```bash
buildozer android release
```

需要配置签名密钥：

```bash
keytool -genkey -v -keystore mykey.keystore -alias myalias -keyalg RSA -keysize 2048 -validity 10000
```

然后在 `buildozer.spec` 中配置：

```ini
android.signing.keystore = mykey.keystore
android.signing.alias = myalias
android.signing.storepass = yourpassword
android.signing.keypass = yourpassword
```

## 界面预览

### 加载界面
- 深色背景配红色装饰
- 中央大字"点"
- 进度条动画
- 标语"一点天惊，点亮人生"

### 主界面
- 三个主要功能按钮
- 导入文件、手动输入、已有点名器
- 底部版本信息

### 点名界面
- 与原版桌面版完全一致
- 星星闪烁动画
- 彩色边角装饰
- 中央名字显示
- 粒子爆炸特效

## 数据存储

- Android: `/sdcard/RollCall/`
- 其他平台: `~/.rollcall/`

存储文件：
- `index.json` - 点名器索引
- `{id}.json` - 点名器数据

## 注意事项

1. **权限**: Android 6.0+ 需要动态申请存储权限
2. **字体**: 使用系统默认中文字体，如需自定义字体请放在项目目录
3. **性能**: 大量人名（>1000）可能影响性能
4. **兼容性**: 最低支持Android 5.0 (API 21)

## 更新日志

### v6.0.0.0
- 初始Android版本发布
- 完整复刻桌面版功能
- 新增多种导入方式
- 优化移动端操作体验

## 许可证

MIT License

## 作者

一点天惊出品

## 联系方式

如有问题或建议，欢迎反馈！
