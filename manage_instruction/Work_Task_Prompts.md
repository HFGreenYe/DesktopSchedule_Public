# Work Task Prompts

用途：保存当前由主窗口确认、可交给执行窗口直接执行的最终提示词。

---

# 当前任务：Markdown 保存路径与真实文件落盘已完成

只修改 `src/ui/popups/export_schedule_panel.py`，除非既有 service 接口存在阻塞才允许小幅修改 `src/services/schedule_export_service.py`。点击导出按钮时读取当前格式：Markdown 弹出系统保存文件对话框，保证目标后缀为 `.md`，并调用既有 `ScheduleExportService.write_markdown()` 按当前内容类型和日 / 周 / 月 / 全部范围真实写入 UTF-8 文件；用户取消时静默返回，成功与失败提供明确反馈。PDF / PNG 仅提示尚未接入，不生成占位文件。不得修改数据库、payload、查询语义、其他窗口或导出面板布局。完成后执行静态语法检查、纯 service 临时目录写入验证和 `git diff --check`，并更新工作日志与最终构想进度。

执行状态：已完成。下一轮提示词应在 PDF 中文字体、分页和输出依赖方案确认后生成。
