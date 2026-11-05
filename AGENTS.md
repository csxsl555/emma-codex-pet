# 项目约定

这是 Emma 桌宠的独立发布副本，原始制作材料另行保留。

- `package/`：供 Codex 加载的 pet.json 和 spritesheet.png。
- `preview/`：README 动画预览、各状态预览、帧检查图和打包记录。
- `source/`：最终生成源图、主形象及对应提示词；不收录用户参考图或旧草稿。
- `scripts/`：构建、预览、校验、打包和安装脚本，使用相对路径或运行时用户目录。
- `dist/`：可下载桌宠 ZIP；新打包保留版本，不自动删除。
- `validation.json`：相对路径校验报告。
- `README.md`、`NOTICE.md`：安装、重建、形象来源与使用说明。
- `requirements.txt`：构建依赖；安装现成桌宠无需 Python。
- `.gitignore`：忽略虚拟环境、缓存、凭据和安装测试产物。

不得提交凭据、用户名绝对路径、第三方参考图片、缓存或未选中草稿。修改后运行 `python scripts/validate_pet.py`；涉及构建时运行构建、预览并检查帧表。远程创建、push 和公开发布必须等用户确认具体仓库和可见性。禁止自动删除文件或覆盖已安装桌宠。
