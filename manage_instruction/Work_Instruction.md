# Work Instruction

用途：记录当前待执行的小工单阶段合同。执行窗口只能根据主窗口确认后的最终提示词行动。

---

# 当前状态：Markdown 保存路径与真实落盘已完成

允许修改：

- `src/ui/popups/export_schedule_panel.py`
- 必要时小幅修正 `src/services/schedule_export_service.py`
- 当前阶段管理文档

必须完成：

- 导出按钮根据当前格式执行分发。
- Markdown 弹出系统保存文件对话框，默认使用 `.md` 文件名。
- 用户输入其他或缺失后缀时统一落为 `.md`。
- 调用既有 `ScheduleExportService.write_markdown()` 写入 UTF-8 文件。
- 取消保存静默返回；成功给出完成提示；异常给出失败原因。
- PDF / PNG 当前只提示尚未接入，不得伪造文件。

禁止范围：

- 不修改数据库模型、Repository 查询语义或日程写入逻辑。
- 不把 Markdown 拼装复制到 UI。
- 不实现 PDF、PNG、背景图片、导出历史或自动打开文件。
- 不顺手重构导出面板布局和其他窗口。

验收：

- 某日 / 某周 / 某月 / 全部与三种内容类型继续复用当前预览选项。
- 取消对话框不落盘。
- 无后缀或错误后缀最终生成 `.md`。
- 导出文件为 UTF-8，内容与同选项 Markdown 预览来源一致。
- PDF / PNG 点击不会产生错误格式文件。
- Python 静态语法检查和纯 service 临时目录写入验证通过。

完成结果：

- Markdown 保存对话框、后缀规范化、真实写入和结果反馈已接入。
- PDF / PNG 仍只提示尚未接入。
- 下一轮施工前需为 PDF 建立新的允许范围、禁止范围和验收合同。
