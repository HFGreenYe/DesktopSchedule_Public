# Work Instruction

用途：记录当前待执行的小工单阶段合同。执行窗口只能根据主窗口确认后的最终提示词行动。

---

# 当前状态：ReportLab PDF 真实导出与分页预览已完成

允许修改：

- `src/services/schedule_pdf_exporter.py`
- `src/services/schedule_pdf_preview_service.py`
- `src/services/schedule_export_service.py`
- `src/ui/popups/export_schedule_panel.py`
- `requirements.txt`
- 当前阶段管理文档

必须完成：

- 使用 ReportLab 基于既有 `ExportPayload` 生成 A4 PDF。
- PDF 保存对话框提供默认 `.pdf` 文件名并规范化错误或缺失后缀。
- 内容类型和日 / 周 / 月 / 全部范围继续复用 `ExportOptions`。
- 纯色 / 渐变背景、三类字体与颜色、加粗和斜体真实进入 PDF。
- 中文字体嵌入后可显示、搜索和复制；英文字体选择时中文使用稳定回退字体。
- 普通卡片不在页尾截断；仅单卡超过整页时生成带“续”标记的续卡。
- 取消保存静默返回；成功提示文件名；异常展示失败原因。
- PDF 设置变化后使用约 `300ms` 防抖，后台任务串行生成临时 PDF，只加载最新结果并自动清理旧文件。
- 内嵌预览显示真实第一页缩略图和总页数；放大预览使用 `QPdfDocument / QPdfView` 多页模式显示真实页框、分页和页码。

禁止范围：

- 不修改数据库、Repository、导出 payload 字段和查询语义。
- 不在导出面板内实现 PDF 排版逻辑。
- 不实现 PNG、背景图片、导出历史、默认路径持久化或自动打开文件。
- 不顺手重构导出面板布局和其他窗口。

验收：

- 项目 `.venv` 可导入 `reportlab==4.4.9`。
- 8 种弹窗字体、纯色 / 渐变、三类颜色、加粗和斜体均可生成文件。
- 空结果、普通多页和超长单卡均能完成导出。
- PDF 文本提取包含页眉、首条、末条和中文详情。
- 离屏实例化真实导出弹窗后，PDF / Markdown 后缀、取消保存和结果分发正确。
- 防抖、串行、旧任务失效、临时文件清理、多页跳转和第一页缩略图通过独立回归。
- 全量 Python AST 检查与 `git diff --check` 通过。

完成结果：

- PDF 保存、ReportLab 排版、字体回退、搜索文本和分页策略已接入。
- 当前 PDF 会真实使用导出弹窗中所有已启用的 PDF 选项；尺寸仍按设计只属于 PNG。
- 原 HTML 近似 PDF 预览已移除；预览和保存现在共用同一 ReportLab 排版器。
- PNG 仍只提示尚未接入，下一轮施工前需建立独立合同。
