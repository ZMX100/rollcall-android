[app]
# 应用标题
 title = 一点天惊点名器

# 包名
package.name = rollcall

# 包域名
package.domain = org.yidiantianjing

# 源文件
source.dir = .

# 包含的文件
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# 版本号
version = 6.0.0.0

# 最低Android API版本
android.api = 21

# 目标Android API版本
android.sdk = 33

# NDK版本
android.ndk = 25b

# 支持的Android架构
android.archs = armeabi-v7a, arm64-v8a

# 依赖库
requirements = python3,kivy==2.3.1,openpyxl,xlrd,pillow

[buildozer]
# 日志级别 (0 = 错误, 1 = 警告, 2 = 信息, 3 = 调试)
log_level = 2

# 警告模式
warn_on_root = 1

# 构建目录
build_dir = ./.buildozer

# 打包模式 (debug/release)
build_mode = debug

# 应用图标
# android.icon.filename = %(source.dir)s/icon.png

# 权限
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Android特定设置
android.gradle_dependencies = com.android.support:support-compat:28.0.0

# 屏幕方向 (portrait/landscape/all)
android.orientation = portrait

# 全屏模式
android.fullscreen = 0

# 签名设置 (release模式需要)
# android.signing.keystore = mykey.keystore
# android.signing.alias = myalias
# android.signing.storepass = mypassword
# android.signing.keypass = mypassword

[ios]
# iOS特定设置
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

[app:android]
# Android特定设置
android.api = 21
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.private_storage = True
android.skip_update = False
android.accept_sdk_license = True

# 启用Android日志
android.logcat_filters = *:S python:D

# 应用名称
android.app_name = 一点天惊点名器

# 应用包名
android.package = org.yidiantianjing.rollcall

# 应用版本代码
android.numeric_version = 6000000

# 应用版本名称
android.version = 6.0.0.0

# 应用图标
# android.icon.ldpi = %(source.dir)s/icon_ldpi.png
# android.icon.mdpi = %(source.dir)s/icon_mdpi.png
# android.icon.hdpi = %(source.dir)s/icon_hdpi.png
# android.icon.xhdpi = %(source.dir)s/icon_xhdpi.png
# android.icon.xxhdpi = %(source.dir)s/icon_xxhdpi.png
# android.icon.xxxhdpi = %(source.dir)s/icon_xxxhdpi.png

# 启动画面
# android.presplash.color = #1a1a2e
# android.presplash.landscape = %(source.dir)s/presplash_landscape.png
# android.presplash.portrait = %(source.dir)s/presplash_portrait.png

# 权限
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 功能
android.features = android.hardware.screen.portrait

# 依赖项
android.gradle_dependencies = com.android.support:support-compat:28.0.0

# 添加Java类
# android.add_src =

# 添加资源
# android.add_resources =

# 添加资产
# android.add_assets =

# 添加库
# android.add_libs_armeabi_v7a =
# android.add_libs_arm64_v8a =
# android.add_libs_x86 =
# android.add_libs_x86_64 =

# 添加AAR
# android.add_aars =

# 添加JAR
# android.add_jars =

# 添加Gradle仓库
# android.add_repositories =

# 添加Gradle依赖
# android.gradle_dependencies =

# 添加P4A配方
# android.p4a_recipes =

# P4A本地配方
# android.p4a_local_recipes =

# P4A分支
# android.p4a_branch = master

# P4A端口
# android.p4a_port =

# P4A推送组
# android.p4a_push_group =

# P4A本地依赖
# android.p4a_local_deps =

# P4A本地依赖递归
# android.p4a_local_deps_recursive =

# 启用AndroidX
android.enable_androidx = True

# 使用Gradle 8
android.gradle_plugin_version = 8.0.0

# 使用Java 17
android.java_version = 17

[app:ios]
# iOS特定设置
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

# 代码签名身份
# ios.codesign.allowed = False
# ios.codesign.identity = iPhone Developer: <lastname> <firstname> (<hexstring>)

# 开发团队
# ios.codesign.developer_team =

# 配置文件
# ios.codesign.provisioning_profile =
