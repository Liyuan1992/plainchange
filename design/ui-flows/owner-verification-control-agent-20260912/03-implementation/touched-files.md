# Touched Files

| File | Reason | Round |
| --- | --- | --- |
| `src/plainchange/verification.py` | 新增固定范围、哈希绑定的验证收据和负责人控制面投影 | 1 |
| `src/plainchange/generator_contract.py` | 只接收结构化 `actual_test_receipt` | 1 |
| `src/plainchange/validator.py` | 将收据带入已校验说明 | 1 |
| `src/plainchange/review_model.py` | 生成已完成检查、缺口和负责人决策 | 1 |
| `src/plainchange/model_adapter.py` | 把验证收据送入模型上下文并规定其事实优先级 | 1 |
| `src/plainchange/templates/review.js` | 把旧三卡改为验证控制面 | 1 |
| `src/plainchange/templates/review.css` | 新增控制面布局与窄屏规则 | 1 |
| `src/plainchange/report_localization.py` | 纳入缺口原因和验证方法的译文投影 | 1 |
| `tests/test_verification.py` | 验证收据、防篡改和冲突优先级回归 | 1 |
| `tests/test_generator_contract.py` | 验证收据入包回归 | 1 |
| `tests/test_review_model.py` | 负责人控制面回归 | 1 |
| `tests/test_html_renderer.py` | 离线页面结构回归 | 1 |
