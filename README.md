# ManaMetal-Chess-Auto

智慧试炼按 F8 自动执白，使用原棋杖交互与原版棋盘规则。

- 独立模组版本：**1.0.1**。
- Minecraft **1.7.10 / Forge**；仅需客户端安装，服务器无需安装本工具。
- 运行时需要魔法金属及其前置（当前工作区版本为魔法金属 8.0.7、Muya 1.11.1）。
- 作者：**白狐铃 / ArcticFoxLing**。
- 许可证：[MIT](LICENSE)，Copyright (c) 2026 ArcticFoxLing。

## 与合集的关系

此功能已合并进 [FoxFoxM3Tools／狐狐魔金小工具](https://github.com/ArcticFoxLing/FoxFoxM3Tools)。本仓库保存原独立工程，便于阅读、构建和单独使用；安装包含此功能的合集版本时，请移出本独立模组，避免重复注册与重复操作。

保留独立版的功能与版本，不把合集中的其他功能一并安装。

操作步骤、限制与原有验证范围见 [使用说明](使用说明.md)。

## 源码与构建

`src/` 保存模组源码与资源；现有测试保留在 `tests/`、`client-tests/` 或 `server-tests/`。仓库不包含游戏文件、第三方模组 JAR、反编译源码、测试存档或构建缓存。`src/project/.../*Access.java`（如存在）是本工具编写的访问桥接类。

需要 **Python 3.9+** 与支持 `javac --release 8` 的 **JDK**。当前构建使用 JDK 21，输出 Java 8 字节码。依赖需另行准备，使用 `FOXFOX_WORKSPACE` 指定其目录：

```powershell
$env:FOXFOX_WORKSPACE = 'D:\MinecraftWorkspace'
python build.py
```

依赖工作区沿用原工程布局：

```text
MinecraftWorkspace/
  FoxFoxAccessories/tools/forge-1.7.10-srg.jar
  .minecraft/
    libraries/  # ASM、LaunchWrapper、LWJGL 及原客户端运行库
    mods/manametalmod-8.0.7.jar
    mods/[Muya]Muya_1.11.1.jar
  fcwqmmmserver/mods/manametalmod-8.0.7.jar
```

`forge-1.7.10-srg.jar` 是含 Minecraft/Forge 类和 SRG 名称的编译依赖，普通 Forge 安装器不能直接替代。部分脚本另支持 `FORGE_SRG_JAR`、`MANAMETAL_JAR`、`MUYA_JAR` 或原有工作区变量，详见脚本。成功后 JAR 输出到 `dist/`，本地验证记录输出到 `build/`；它们均由 `.gitignore` 排除。

## 测试与发布

已有非图形测试可按 [使用说明](使用说明.md) 运行；隔离客户端／服务器测试需要原工作区的启动配置、资源和测试服务器模板，不随源码发布。`client-tests/run.py` 在启动前将隔离测试目录的总音量与所有声音分类设为零。不得修改实际游玩客户端音量。

`package.py` 按原项目要求核验构建及运行记录；完成对应测试后可生成带许可证的发布包。源码开源发布不代表在其他魔法金属版本或其他整合包中完成兼容验证。第三方运行与构建依赖遵循各自许可证。
