# Work Log

用途：记录当前活动小工单的执行过程、验证结果和待复核事项。

---

# 当前状态：Markdown 真实落盘已完成

## 2026-07-16：方案审查

- 已确认 `ScheduleExportService` 具备统一 payload、Markdown 渲染和 `write_markdown(file_path, options)` UTF-8 写入入口。
- 当前缺口仅为导出按钮的格式分发、系统保存路径、`.md` 后缀规范化及成功 / 失败反馈。
- 决定不修改数据库、Repository、导出 payload 和 Markdown 结构；PDF / PNG 留在后续独立小工单。

## 2026-07-16：实现与验证

- `ExportSchedulePanel` 已将既有 `export_requested` 信号接入真实格式分发。
- Markdown 使用系统保存文件对话框；默认文件名按内容类型和日 / 周 / 月 / 全部范围生成，用户输入其他或缺失后缀时统一改为 `.md`。
- 文件写入复用 `ScheduleExportService.write_markdown()`；取消保存静默返回，成功显示文件名，异常使用错误对话框展示原因。
- PDF / PNG 当前只显示“尚未接入”提示，不生成占位文件。
- 验证结果：85 个 Python 文件 AST 解析通过，语法错误为 0；使用纯内存 repository 和临时目录完成 UTF-8 Markdown 真实写入，中文标题和详情读取正确；`git diff --check` 通过。
- 复核确认项目 `.venv` 正常可用，解释器为 Python 3.11.9，PyQt6 可正常导入；此前 `Unable to create process` 来自沙盒内无法访问虚拟环境依赖的用户目录基础解释器路径，并非虚拟环境失效。
- 使用项目 `.venv` 和 `QT_QPA_PLATFORM=offscreen` 实例化真实 `ExportSchedulePanel`：模拟选择 `.txt` 路径后正确生成 `.md`，UTF-8 文件以 `# 日程导出` 开头；取消保存不落盘；选择 PDF 时只显示“PDF 导出尚未接入”，三项烟测均通过。
