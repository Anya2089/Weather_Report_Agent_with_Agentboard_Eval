# Weather Agent

基于AgentBoard框架的智能天气查询系统，能够处理各种天气相关查询并生成结构化报告。该系统通过多维度评估指标验证了智能体在天气查询任务中的优秀表现，为智能体技术的实际应用提供了可靠的技术基础。

## 项目概述

Weather Agent是一个基于大型语言模型的智能天气查询系统，集成了完整的数据获取、处理和报告生成能力。系统能够理解自然语言形式的天气查询，调用适当的工具函数获取实时天气数据，并生成多格式的专业天气报告。该项目基于AgentBoard评估框架构建，通过严格的多维度指标评估验证了系统的可靠性和实用性。

**核心能力**：
- 自然语言天气查询理解
- 多源天气数据获取和整合
- 多格式报告生成（JSON、Markdown、HTML、Text）
- 智能文件管理和组织
- 完整的错误处理和恢复机制

## 技术架构

Weather Agent采用分层架构设计，通过智能体层、环境层、工具层、提示层和评估层的协同工作，实现了从用户查询到结果输出的完整工作流程。

**架构层次**：
- **智能体层**：基于VanillaAgent实现，负责任务理解和执行策略制定
- **环境层**：WeatherEnv处理动作路由、格式验证和状态管理
- **工具层**：WeatherTools提供API调用、数据处理和报告生成功能
- **提示层**：结构化提示模板指导智能体行为
- **评估层**：多维度指标体系评估系统性能

**数据流程**：
```
用户查询 → 智能体理解 → 动作生成 → 环境路由 → 工具执行 → 数据处理 → 报告生成 → 结果返回
```

## 代码结构

系统采用模块化设计，核心组件职责明确，便于维护和扩展。

```
weather-agent/
├── agentboard/                        # AgentBoard框架核心
│   ├── agents/                        # 智能体实现
│   │   ├── base_agent.py              # 智能体基类
│   │   └── vanilla_agent.py           # ★ Weather Agent智能体实现
│   ├── environment/                   # 环境实现
│   │   ├── base_env.py                # 环境基类
│   │   └── weather_env.py             # ★ Weather环境（动作路由、状态管理）
│   ├── llm/                           # LLM接口层
│   │   ├── openai_gpt.py              # ⚠️ OpenAI模型接口
│   │   ├── claude.py                  # ⚠️ Claude模型接口
│   │   ├── azure_gpt.py               # ⚠️ Azure模型接口
│   │   └── bedrock_claude.py          # ⚠️ AWS Bedrock接口
│   ├── prompts/                       # 提示模板
│   │   └── VanillaAgent/              
│   │       └── weather_prompt.json    # ★ Weather Agent提示模板
│   ├── tasks/                         # 任务评估
│   │   ├── base_task.py               # 任务基类
│   │   └── tool.py                    # ★ Weather任务评估实现
│   ├── utils/                         # 工具函数
│   │   ├── weather/                   
│   │   │   └── weather_tools.py       # ★ Weather工具集（API调用、报告生成）
│   │   ├── tool/
│   │   │   └── helpers.py             # ★ 动作解析器（格式标准化）
│   │   └── logging/                   # 日志系统
│   │       ├── agent_logger.py        # 智能体执行日志
│   │       └── logger.py              # 任务评估日志
│   └── eval_main.py                   # ★ 评估入口脚本
├── data/                              # 测试数据
│   └── tool-query/                    
│       └── test.jsonl                 # ★ Weather测试用例
├── eval_configs/                      # 评估配置
│   └── main_results_all_tasks.yaml    # ★ 评估参数配置
├── results/                           # 评估结果
├── scripts/                           # 执行脚本
│   └── evaluate.sh                    # ★ 评估脚本
├── requirements.txt                   # Python依赖

```

**核心组件说明**（标★为Weather Agent核心组件）：

**必需的核心文件**：
1. `weather_env.py`: Weather环境实现，处理智能体动作，调用工具函数
2. `weather_tools.py`: Weather工具集实现，提供天气查询和报告生成功能
3. `vanilla_agent.py`: 基础智能体实现，Weather Agent使用此智能体
4. `weather_prompt.json`: Weather Agent的提示模板和示例
5. `tool.py`: 工具任务评估实现，包括Weather任务的多维度评估
6. `helpers.py`: 动作解析器，负责格式标准化和参数提取
7. `eval_main.py`: 评估入口脚本，协调各组件完成评估流程

**非必需的组件**：
- 其他任务环境（alfworld、browser_env、WebShop等）
- 其他任务工具集（academia、movie、sheet、todo等）
- 调试和测试脚本（debug_agent.py、test_*.py等）

## 评估指标体系

Weather Agent采用AgentBoard的多维度评估体系，通过四个核心指标全面评估智能体的任务执行能力。基于Claude-3.7的实际测试结果显示，系统在所有关键指标上都达到了优秀水平。

**核心评估指标**：

**Success Rate（成功率）**：衡量智能体完全成功完成任务的比例。计算方法为成功完成的任务数除以总任务数，取值范围0.0-1.0。该指标采用严格的二元判断，只有100%完成的任务才被认为成功。测试结果显示Weather Agent达到了1.0（100%）的完美成功率。

**Progress Rate（进度率）**：评估智能体在任务执行过程中的进展程度。通过子目标离散分数方法计算，即完成的子目标数除以总子目标数。该指标能够反映智能体的部分进展，即使任务未完全成功也能体现执行能力。测试结果同样达到1.0（100%）。

**Grounding Accuracy（基础准确率）**：测量智能体执行动作的准确性。通过统计未返回错误信息的动作比例计算，即正确执行的步骤数除以总步骤数。该指标反映智能体理解和执行具体操作的能力。测试结果为0.913（91.3%），表明智能体在动作执行方面表现良好。

**Score State（得分状态）**：记录智能体在任务执行过程中每个关键步骤的得分变化。采用元组列表格式`[(step_id, score), ...]`，只在得分提高时记录。该指标用于分析智能体的学习曲线和进展模式，帮助识别任务完成的关键节点。

**测试结果分析**：
```json
{
  "success_rate": 1.0,
  "progress_rate": 1.0, 
  "grounding_acc": 0.9133333333333333,
  "success_rate_easy": 1.0,
  "progress_rate_easy": 1.0
}
```

测试结果表明Weather Agent在简单任务上表现完美，所有任务都能成功完成。Grounding Accuracy为91.3%，主要反映了部分API调用参数的细微差异和数据格式处理的小幅偏差，但不影响最终任务完成。

## 功能演示

Weather Agent支持多种类型的天气查询，能够处理从简单的当前天气查询到复杂的多维度分析任务。

**基础天气查询**：
- "What's the weather like in New York today?" - 查询纽约今日天气
- "Tell me the current temperature in London" - 获取伦敦当前温度
- "How's the air quality in Beijing?" - 查询北京空气质量

**历史天气分析**：
- "What was the temperature in Tokyo on January 1st, 2023?" - 查询东京历史温度
- "How much did it rain in Paris last week?" - 分析巴黎降雨情况
- "Show me the weather trend for Shanghai in the past month" - 上海天气趋势分析

**预测和对比查询**：
- "Will it snow in Moscow next week?" - 莫斯科降雪预测
- "Compare the air quality between Los Angeles and San Francisco" - 城市空气质量对比
- "What will the temperature be in Sydney tomorrow?" - 悉尼明日温度预测

**报告生成示例**：
系统能够生成多格式的结构化报告，包括JSON格式的数据结构、Markdown格式的人类友好报告、HTML格式的网页展示和Text格式的简洁摘要。所有报告都包含完整的天气数据、分析结果和实用建议。

## 安装与配置

系统安装需要Python 3.8+环境和相关依赖包，同时需要配置必要的API密钥以访问天气数据和LLM服务。

**环境准备**：
```bash
# 克隆仓库
git clone https:*
cd weather-agent

# 安装依赖
pip install -r requirements.txt
```

**API密钥配置**：
```bash
# 复制环境变量模板
cp .template_env .env

# 编辑.env文件，添加必要的API密钥
# OPENAI_API_KEY=your_openai_api_key
# ANTHROPIC_API_KEY=your_anthropic_api_key
# AWS_ACCESS_KEY_ID=your_aws_access_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

**验证安装**：
```bash
# 运行简单测试
python agentboard/eval_main.py --cfg-path eval_configs/main_results_all_tasks.yaml --tasks tool-query --model claude --log_path ./test_results
```

## 使用方法

系统提供了灵活的评估和测试方式，支持不同模型和配置的对比测试。

**标准评估流程**：
```bash
# 使用评估脚本
./scripts/evaluate.sh --model claude --tasks tool-query

# 直接使用Python
python agentboard/eval_main.py \
    --cfg-path eval_configs/main_results_all_tasks.yaml \
    --tasks tool-query \
    --model claude-3-sonnet-20240229 \
    --log_path ./results/weather-test \
    --project_name weather-agent-evaluation
```

**自定义配置评估**：
```bash
# 指定特定模型和参数
python agentboard/eval_main.py \
    --cfg-path eval_configs/main_results_all_tasks.yaml \
    --tasks tool-query \
    --model gpt-3.5-turbo-0613 \
    --max_num_steps 15 \
    --log_path ./results/gpt35-weather-test
```

**结果查看**：
评估结果保存在指定的log_path目录下，包含总体评估结果、详细任务结果和完整的执行日志。结果文件包括`all_results.txt`（总体结果）、`tool-query.txt`（Weather任务结果）和`logs/tool-query.jsonl`（详细执行日志）。

## 开发指南

系统采用模块化设计，支持功能扩展和自定义开发。开发者可以通过扩展工具集、修改提示模板或调整评估指标来适应特定需求。

**扩展天气工具**：
在`agentboard/utils/weather/weather_tools.py`中添加新的天气查询功能，遵循现有的函数签名和返回格式。新工具需要在`weather_env.py`中注册相应的动作路由。

**自定义提示模板**：
修改`agentboard/prompts/VanillaAgent/weather_prompt.json`中的指令和示例，可以调整智能体的行为模式和响应风格。提示模板支持多语言和特定领域的定制。

**调整评估指标**：
在`agentboard/tasks/tool.py`中修改评估逻辑，可以添加新的评估维度或调整现有指标的计算方法。支持自定义子目标定义和权重分配。

**性能优化建议**：
- 启用API调用缓存减少重复请求
- 优化数据处理流程提高响应速度
- 实现异步处理支持并发查询
- 添加错误重试机制提高可靠性

## 故障排除

系统提供了完善的日志记录和错误诊断机制，帮助快速定位和解决问题。

**常见问题及解决方案**：

**API密钥错误**：检查.env文件中的密钥配置，确保密钥有效且具有相应权限。可以通过单独的API测试脚本验证密钥可用性。

**网络连接问题**：确认网络连接正常，检查防火墙设置。某些API服务可能需要特定的网络配置或代理设置。

**数据格式错误**：检查测试数据格式是否符合要求，特别是JSON格式的正确性。可以使用JSON验证工具检查数据文件。

**内存不足**：对于大规模测试，可能需要调整批处理大小或增加系统内存。可以通过分批处理或流式处理来优化内存使用。

**调试技巧**：
- 启用详细日志记录查看执行过程
- 使用单个测试用例进行问题隔离
- 检查API调用的请求和响应内容
- 验证环境变量和配置文件的正确性



