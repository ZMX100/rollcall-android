# 字体目录

将支持 emoji 的字体文件放在此目录，例如：

1. **NotoColorEmoji.ttf** - Google Noto Emoji 字体（推荐）
   - 下载地址：https://github.com/googlefonts/noto-emoji/tree/main/fonts

2. **Segoe UI Emoji** - Windows 自带（仅Windows可用）

3. **Apple Color Emoji** - macOS/iOS 自带

4. **NotoSansCJKsc-Regular.otf** - 中文支持
   - 下载地址：https://github.com/googlefonts/noto-cjk

## Android 打包注意

在 buildozer.spec 中添加：
```
source.include_exts = py,png,jpg,kv,atlas,ttf,otf
```

字体文件会被自动打包到 APK 中。
