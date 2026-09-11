(() => {
  "use strict";

  const SUPPORTED = Object.freeze(["zh-CN", "en"]);
  const STORAGE_KEY = "plainchange.review.language";
  const HASH_PREFIX = "plainchange-lang=";
  const EN = Object.freeze({
    "基础证据模式：还没有让模型理解这个软件": "Basic evidence mode: the model has not interpreted this software",
    "下面只展示固定代码事实、结构线索和未知项。它不能替代完整的业务理解，也不应被当成最终结论。": "Only fixed code facts, structural clues, and unknowns are shown below. This is not a substitute for complete business understanding and must not be treated as a final conclusion.",
    "实现已展开": "Implementation expanded",
    "查看修改前存在的职责和确定性代码关联；新增职责在此视图中不会出现。": "View responsibilities and deterministic code relationships before the change. Newly added responsibilities do not appear in this view.",
    "查看修改后的职责和确定性代码关联；点击任一节点查看证据边界。": "View responsibilities and deterministic code relationships after the change. Select a node to inspect the limits of its evidence.",
    "只显示新增、移除、改变或有关联的节点；未变化上下文被收起。": "Show only added, removed, changed or related nodes. Unchanged context is collapsed.",
    "代码直接关联": "Direct code relationship",
    "查看已有任务线索": "View available task context",
    "不调用模型，不消耗额外 Token": "No model call or extra tokens",
    "用户原话": "User quotation",
    "用户实际说过的内容": "What the user actually said",
    "← 被依赖": "← Used by",
    "依赖 →": "Depends on →",
    "查看原始结论": "View original conclusion",
    "变": "Δ", "因": "?", "及": "↗", "注": "!", "证": "≡",
    "责": "•", "前": "←", "出": "↗", "后": "→", "改": "Δ", "据": "≡", "人": "•", "影": "↗",
    "：项目自己这样描述": ": How the project describes itself",
    "：代码里确实有相关位置": ": Relevant locations were found in the code",
    "AI 变化说明": "AI change review",
    "查看方式": "View",
    "变化解读": "Change review",
    "整体架构": "System architecture",
    "本次变化状态": "Change status",
    "这次改动的负责人摘要": "Owner summary of this change",
    "一句话结论": "Bottom line",
    "负责人需要掌握的三个结论": "Three conclusions the owner needs",
    "查看完整说明": "View the complete explanation",
    "五个问题与完整依据": "Five questions and their evidence",
    "软件负责人需要回答的五个问题": "Five questions for the software owner",
    "为什么这么判断？查看技术细节": "Why this conclusion? View technical details",
    "四个关键问题": "Four key questions",
    "变化路径与节点说明": "Change paths and node explanations",
    "中文变化影响图": "Change impact map",
    "改变从哪里发生，又关联到哪里": "Where the change happened and what it connects to",
    "默认显示变更后的确定性代码关联；点击节点查看证据边界。": "The default view shows deterministic code relationships after the change. Select a node to inspect its evidence boundary.",
    "变化视图": "Change view",
    "变更前": "Before",
    "变更后": "After",
    "只看差异": "Changes only",
    "代码变化关联路径": "Code-change relationship paths",
    "这里只证明代码关联，不证明这些功能都在运行时受到影响。": "This proves code relationships only; it does not prove that all of these functions are affected at runtime.",
    "当前节点说明": "Selected-node explanation",
    "当前查看": "Currently viewing",
    "请选择一个职责节点": "Select a responsibility node",
    "关闭节点说明": "Close node explanation",
    "技术依据": "Technical evidence",
    "查看技术依据": "View technical evidence",
    "这个软件怎么工作": "How this software works",
    "收起当前步骤": "Collapse this step",
    "收起当前能力": "Collapse this capability",
    "图中状态说明": "Map-state legend",
    "深蓝边框 = 当前查看": "Dark blue border = currently selected",
    "橙色 = 本次改动": "Orange = changed in this update",
    "信息来源说明": "Source legend",
    "来自项目说明": "From project documentation",
    "项目自己这样描述": "How the project describes itself",
    "找到对应代码": "Matching code found",
    "代码里确实有相关位置": "A related location exists in the fixed source",
    "模型候选理解": "Model-generated candidate understanding",
    "已通过本地来源和路径校验，仍不是运行事实": "Locally checked against allowed sources and paths; still not runtime proof",
    "：已通过本地来源和路径校验，仍不是运行事实": ": Locally checked against allowed sources and paths; still not runtime proof",
    "可点击的软件工作图": "Interactive software workflow",
    "当前工作步骤说明": "Current workflow-step explanation",
    "查看步骤之间的完整关系": "View all relationships between steps",
    "完整工作关系说明": "Complete workflow relationships",
    "查看技术实现结构": "View technical implementation",
    "整体系统结构图": "Whole-system structure",
    "先看系统如何工作，再核对实现结构": "Understand the system flow, then inspect its implementation",
    "结构覆盖": "Structure coverage",
    "可展开的整体架构图": "Expandable system architecture map",
    "系统工作流": "System workflow",
    "系统工作流关系图": "System workflow map",
    "外部输入": "External input",
    "由人或 Git 提供": "Provided by a person or Git",
    "系统自动处理": "System processing",
    "只读、可复核": "Read-only and reviewable",
    "人工决定": "Human decision",
    "系统不可越过": "The system cannot bypass this",
    "系统工作流关系说明": "System workflow relationships",
    "展开的静态实现": "Expanded static implementation",
    "当前架构说明": "Current architecture explanation",
    "本地单文件 · 只读 · 无网络请求": "Local single file · read-only · no network requests",
    "软件变化掌控报告": "Software change control report",
    "这次改了什么": "What changed",
    "会影响我现在的软件吗？": "Could this affect my software now?",
    "我需要担心什么？": "What should I be concerned about?",
    "我现在该怎么办？": "What should I do now?",
    "以前": "Before",
    "现在": "Now",
    "很可能有变化": "Very likely affected",
    "可能有变化": "Possibly affected",
    "可能受影响": "Possibly affected",
    "已确认": "Confirmed",
    "接下来做": "Next action",
    "建议行动": "Suggested action",
    "范围判断": "Scope assessment",
    "项目说明": "Project description",
    "项目说明与代码对账": "Project description checked against code",
    "能力说明与代码对账": "Capability description checked against code",
    "下面是从固定版本项目说明和代码位置提炼的能力结构；它们可以被不同入口组合使用，不代表运行顺序。": "This capability structure is derived from fixed project documentation and code locations. Different entry points may combine these capabilities; their placement does not imply runtime order.",
    "先看项目的主要能力，再展开项目说明与代码位置；这些能力没有固定先后顺序。": "Start with the project's main capabilities, then expand their documentation and code locations. These capabilities have no fixed order.",
    "代码变化已确认": "Code change confirmed",
    "有独立测试证据": "Independent test evidence available",
    "测试证据不完整": "Test evidence is incomplete",
    "目前没发现": "Not found so far",
    "还没验证": "Not verified",
    "还没判断": "Not assessed yet",
    "这是个什么软件？": "What is this software?",
    "AI 这次主要改变了什么？": "What did AI mainly change?",
    "谁可能感觉到变化？": "Who may notice a change?",
    "谁会感觉到变化？": "Who may notice a change?",
    "还有什么我们不知道？": "What do we still not know?",
    "还有什么不知道？": "What remains unknown?",
    "我接下来该检查什么？": "What should I check next?",
    "先完成两项最小检查：": "Complete these two minimum checks first:",
    "输入进入软件": "Input enters the software",
    "软件接收用户、程序或其他系统交给它的内容。": "The software receives content from a user, program, or another system.",
    "检查并整理输入": "Check and prepare the input",
    "软件把收到的内容整理成主要功能可以处理的形式。": "The software prepares the received content for its main function.",
    "执行主要功能": "Run the main function",
    "软件完成它最主要的处理工作。": "The software performs its main processing work.",
    "返回结果或状态": "Return a result or status",
    "把处理结果、状态或数据交还给调用方。": "Return the processed result, status, or data to the caller.",
    "调用与用户入口": "Calls and user entry points",
    "接收用户、程序或外部系统交给软件的输入。": "Receive input supplied by users, programs, or external systems.",
    "数据与状态": "Data and state",
    "整理软件需要读取、保存或传递的数据。": "Organize data the software reads, stores, or passes on.",
    "主要功能": "Core functions",
    "执行这个软件最主要的处理工作。": "Perform the software's main work.",
    "测试与质量保障": "Testing and quality",
    "检查主要功能是否仍按预期工作。": "Check whether the main functions still work as expected.",
    "说明与工程辅助": "Documentation and engineering support",
    "承载说明、示例、构建和维护工具。": "Contain documentation, examples, build support, and maintenance tools.",
    "还没归类的实现": "Unclassified implementation",
    "当前自动草稿还不能确定这些代码在软件中的作用。": "The automatic draft cannot yet determine the role of this code.",
    "自动候选": "Automatic candidate",
    "没有找到明确的项目工作流程说明，这一步是通用候选，需负责人确认。": "No explicit project workflow was found. This is a generic candidate step that needs owner confirmation.",
    "候选顺序": "Candidate order",
    "没有找到明确的项目流程说明；这是通用候选图，不是项目事实或运行记录。": "No explicit project workflow was found. This is a generic candidate map, not a project fact or runtime trace.",
    "顺序未验证": "Order not verified",
    "没有先后顺序": "No fixed order",
    "从代码结构发现": "Discovered from code structure",
    "在这项能力明确引用的代码范围内，根据固定版本的文件和标识符名称形成候选职责；它不是项目声明或运行验证，仍需负责人确认。": "Within the code scope explicitly referenced by this capability, candidate responsibilities were inferred from file and identifier names at the fixed revision. They are not project declarations or runtime verification and still need owner confirmation.",
    "固定版本代码中存在这一类实现位置，但具体业务含义仍需项目说明或负责人确认。": "This type of implementation exists in the fixed source, but its business meaning still needs project documentation or owner confirmation.",
    "没有项目说明或可识别代码分区支持更具体的能力结构。": "No project documentation or recognizable code area supports a more specific capability structure.",
    "没有项目声明或编排证据支持这组通用候选步骤。": "No project declaration or orchestration evidence supports the order of these generic candidate steps.",
    "这次只完成了代码和结构检查，还没有判断普通用户会不会感觉到变化。": "Only code and structure were checked; whether ordinary users may notice a change has not been assessed.",
    "没有运行行为语义解释，不能把未分析写成“目前没发现”。": "Behavioral interpretation was not run, so an unassessed impact cannot be labelled as 'not found'.",
    "目前没有足够证据确认普通用户已经直接感觉到变化。": "There is not enough evidence to confirm that ordinary users have directly noticed a change.",
    "没有发现不等于已经证明不存在。": "Not finding an impact is not proof that none exists.",
    "还没有运行目标软件验证真实行为。": "The target software has not been run to verify actual behavior.",
    "也没有完成完整的行为语义解释。": "A complete behavioral interpretation has not been performed either.",
    "确认正常情况": "Check the normal case",
    "确认停止条件": "Check the stop condition",
    "确认调用方": "Check existing callers",
    "确认软件工作图": "Confirm the software workflow",
    "确认软件能力图": "Confirm the software capability map",
    "由了解项目的人核对能力结构，修正遗漏或不符合实际业务的地方；不要补写没有证据的先后顺序。": "Have someone who knows the project review the capability structure and correct omissions or mismatches. Do not add an order that lacks evidence.",
    "由了解项目的人核对四步工作图，修正不符合实际业务的地方。": "Have someone who knows the project review the four-step workflow and correct anything that does not match the real software.",
    "验证真实行为": "Verify actual behavior",
    "运行与本次改动最相关的一条用户路径或接口，记录实际结果。": "Run one user path or interface most relevant to this change and record the actual result.",
    "确认高亮位置确实是本次改动所在功能": "Confirm that the highlighted step is where this change belongs",
    "运行一条最重要的真实使用路径": "Run the most important real usage path",
    "这一阶段的结果会被交给下一阶段继续处理。": "The result of this stage is passed to the next stage.",
    "这项能力向使用它的人或其他功能提供对应结果；当前证据不声明固定的下一步。": "This capability provides a result to its users or other functions; the current evidence does not declare a fixed next step.",
    "目前没有证据表明本次修改改变了这一步。": "There is no current evidence that this change modified this step.",
    "现有材料不足以确认谁会直接受到影响。": "The available material is insufficient to identify who may be directly affected.",
    "项目说明和代码位置都不能替代真实运行验证。": "Neither project documentation nor a code location can replace runtime verification.",
    "核对项目说明是否仍与当前软件目标一致": "Check whether the project documentation still matches the software's current purpose",
    "需要确认顺序时，运行或检查真实编排路径": "Run or inspect the real orchestration path when step order matters",
    "核对这项能力通常由哪些入口或其他功能调用": "Check which entry points or other functions normally use this capability",
    "本次变化所在部分": "Area containing this change",
    "固定 Git 版本中的代码证据支持这个结论。": "Code evidence from the fixed Git revisions supports this conclusion.",
    "静态代码事实不能替代实际运行检查。": "Static code facts cannot replace an actual runtime check.",
    "接下来做": "Next action",
    "这是根据当前证据缺口给出的建议，不代表已经检查完成。": "This recommendation follows from the current evidence gaps; it does not mean the check has been completed.",
    "软件掌控层": "Software control layer",
    "先回答软件怎样工作、改了什么和下一步检查什么。": "Answer how the software works, what changed, and what to check next.",
    "解释分析层": "Explanation layer",
    "区分已确认、目前没发现和还没验证。": "Separate confirmed, not found so far, and not verified.",
    "技术证据层": "Technical evidence layer",
    "按需展开固定版本、文件和静态关系。": "Expand fixed revisions, files, and static relationships on demand.",
    "软件工作图是自动候选说明，不是运行时追踪": "The software workflow is an automatic candidate explanation, not a runtime trace",
    "软件能力图是自动候选说明，不是调用顺序或运行时追踪": "The software capability map is an automatic candidate explanation, not call order or a runtime trace",
    "静态代码关系不能证明真实用户影响": "Static code relationships cannot prove real user impact",
    "负责人尚未确认项目业务语义": "The owner has not confirmed the project's business meaning",
    "查看详细验证步骤": "View detailed verification steps",
    "在软件流程中查看 →": "View in the software workflow →",
    "在软件能力图中查看 →": "View in the software capability map →",
    "AI 这次改了这里": "AI changed this step",
    "AI 这次改了这项能力": "AI changed this capability",
    "当前工作步骤": "Current workflow step",
    "当前能力": "Current capability",
    "这项能力变了吗": "Did this capability change?",
    "这次这里变了吗": "Did this step change?",
    "本次改动": "Changed in this update",
    "按当前工作图，这是这一层流程的起点。": "In the current workflow, this is the first step in this layer.",
    "按当前工作图，这是这一层流程的终点。": "In the current workflow, this is the final step in this layer.",
    "前一步": "Previous step",
    "后一步": "Next step",
    "这个步骤负责什么": "What this step is responsible for",
    "这项能力负责什么": "What this capability is responsible for",
    "它从哪里来 / 前一步": "Where it comes from / previous step",
    "它在结构中的位置": "Its place in the capability structure",
    "它会产生什么": "What it produces",
    "它会交给哪里 / 后一步": "Where it goes / next step",
    "它可以怎样被使用": "How it can be used",
    "这次修改发生在哪里": "Where this change occurred",
    "代码依据到哪里": "How far the code evidence goes",
    "查看变化影响与检查建议": "View impact and suggested checks",
    "谁可能受到影响": "Who may be affected",
    "仍然不知道": "Still unknown",
    "你可以检查": "What you can check",
    "从变化页定位到这里": "Located here from the change view",
    "本次改动所在阶段": "Stage changed in this update",
    "本次改动所在能力": "Capability changed in this update",
    "当前系统位置": "Current system location",
    "当前工作图没有声明这个阶段更细的产出。": "The current workflow does not declare a more detailed result for this stage.",
    "当前证据没有把本次修改定位在这个阶段。": "The current evidence does not locate this change in this stage.",
    "当前证据没有把本次修改定位在这项能力。": "The current evidence does not locate this change in this capability.",
    "依据状态未标注": "Evidence status not labelled",
    "当前工作图没有提供更具体的代码依据说明。": "The current workflow provides no more specific code-evidence explanation.",
    "点击左侧这一步，在同一张图里展开详细过程。": "Select this step on the left to expand its details in the same map.",
    "点击查看这项能力的依据": "Select to inspect the evidence for this capability",
    "能力卡片保持在全局结构中，可再次点击收起。": "The capability card remains in the full structure; select it again to collapse it.",
    "点击左侧能力，在全局结构中展开；再次点击即可收起。": "Select the capability on the left to expand it inside the full structure; select it again to collapse it.",
    "暂未识别出更细的内部结构": "No finer internal structure has been identified yet",
    "当前证据只支持这一级，不会为了展示效果重复或编造子节点。": "The current evidence supports only this level; PlainChange will not repeat or invent child nodes for presentation.",
    "接收输入与会话": "Receive input and session context",
    "接收调用方交来的内容，并维护这次交互需要的会话信息。": "Accept content from the caller and maintain the session information needed for this interaction.",
    "准备上下文与已有信息": "Prepare context and existing information",
    "整理本次处理需要的上下文、提示、记忆或已保存信息。": "Assemble the context, prompts, memory, or saved information needed for this work.",
    "判断如何处理": "Decide how to handle the request",
    "根据规则、权限和当前状态判断接下来可以使用哪些能力。": "Use rules, permissions, and current state to decide which capabilities may be used next.",
    "执行实际处理工作": "Run the actual processing work",
    "调用实际处理能力，并协调任务、工具或并行工作。": "Invoke the processing capabilities and coordinate tasks, tools, or parallel work.",
    "整理并交付结果": "Prepare and deliver the result",
    "把处理结果整理成调用方可以接收的形式，并完成必要的交接。": "Prepare the result in a form the caller can receive and complete any required handoff.",
    "记录状态与过程": "Record state and progress",
    "记录处理中产生的状态、事件、缓存或可追踪过程信息。": "Record state, events, caches, or traceable progress produced during processing.",
    "在这项能力明确引用的代码范围内，找到了承担这一职责的固定版本代码位置；仍未运行验证。": "Within the code scope explicitly referenced by this capability, fixed-version code locations were found for this responsibility; runtime behavior remains unverified.",
    "这是并列能力之一；当前证据没有声明固定的前一步。": "This is one of several peer capabilities; the current evidence does not declare a fixed previous step.",
    "它可能被不同入口或其他能力组合使用；当前证据没有声明固定的后一步。": "Different entry points or other capabilities may use it; the current evidence does not declare a fixed next step.",
    "本次改动所在步骤": "Step changed in this update",
    "本次修改定位在当前步骤。": "This change is located in the current step.",
    "技术实现已保留在下方，可按需展开核对。": "The technical implementation is preserved below and can be expanded when needed.",
    "这一步的详细过程": "Details of this step",
    "这项能力的来源与代码依据": "Sources and code evidence for this capability",
    "这项能力内部包含什么": "What this capability contains",
    "总览仍保留在这里": "The overview remains visible",
    "这一步内部怎么连接": "How the details in this step connect",
    "最小检查": "Minimum check",
    "收起任务线索": "Collapse task context",
    "已有任务线索": "Available task context",
    "判断顺序：用户明确提出 → AI 给出解释 → 用户是否确认。三种来源不能混为一谈。": "Reasoning order: the user's request → the AI's explanation → whether the user confirmed it. These three sources must remain distinct.",
    "当前样本没有整体架构快照": "This sample has no whole-system architecture snapshot",
    "已切换到这个软件怎么工作": "Switched to How this software works",
    "已切换到整体架构": "Switched to System architecture",
    "已切换到这次改了什么": "Switched to What changed",
    "已切换到变化解读": "Switched to Change review",
    "待归类": "Unclassified",
    "模块职责尚未确认": "Module responsibility is not confirmed",
    "未归入前述目录的模块，集中保留在这个阅读分组中。": "Modules not matched by the preceding rules are preserved in this reading group.",
    "自动处理": "Automatic processing",
    "可读输出": "Readable output",
    "持久状态": "Persistent state",
    "系统组件": "System component",
    "这项概念在当前静态快照中没有可下钻的代码分区": "This concept has no code group to inspect in the current static snapshot",
    "关系包含循环，已切换为结构化阅读；下方保留全部关系说明。": "The relationships contain a cycle, so the view has switched to structured reading. Every relationship remains listed below.",
    "该图包含分支或汇合，已按关系层级排布；下方保留全部关系说明。": "This map contains branches or joins and is arranged by relationship level. Every relationship remains listed below.",
    "一个工作步骤可能对应多个实现分区；请在右侧核对。": "One workflow step may map to several implementation groups; review them in the inspector.",
    "这一步在系统外部，由人明确决定": "This step is outside the system and requires an explicit human decision",
    "外部输入或状态，不映射为单一代码分区": "External input or state; it does not map to a single code group",
    "主路径（按编号阅读）": "Main path (read by number)",
    "关系说明（按层阅读）": "Relationships (read by layer)",
    "输入如何进入主干": "How inputs enter the main path",
    "关系过于密集，已切换为结构化阅读；下方保留全部关系说明。": "The relationships are too dense, so the view has switched to structured reading. Every relationship remains listed below.",
    "先通过系统工作流理解输入、处理、输出和人工边界；再向下核对冻结源码的静态实现。": "Use the system workflow to understand inputs, processing, outputs, and human boundaries, then inspect the static implementation in the fixed source.",
    "当前配置没有声明系统工作流；以下仅展示冻结源码中的静态代码结构。": "The current profile declares no system workflow. Only static code structure from the fixed source is shown below.",
    "展开的静态实现": "Expanded static implementation",
    "下列子域由目标配置归类；关系仅汇总当前冻结源码中已有的静态 import。": "The target profile groups these subdomains. Relationships summarize only static imports in the fixed source.",
    "这不是运行时调用顺序。动态注入、网络、数据库和部署关系仍需要独立证据。": "This is not runtime call order. Dynamic injection, network, database, and deployment relationships need separate evidence.",
    "当前快照没有跨子域静态 import；每个子域内部关系仍可在右侧按需核对。": "The snapshot has no cross-subdomain static imports. Internal relationships remain available in the inspector.",
    "直接关系 · 点击可单独追踪": "Direct relationships · select one to trace it",
    "箭头表示静态 import 方向，不代表运行先后。": "Arrows show static import direction, not runtime order.",
    "蓝色：它依赖谁 →": "Blue: what it depends on →",
    "琥珀：← 谁依赖它": "Amber: ← what depends on it",
    "路径未知": "Path unknown",
    "当前模块": "Current module",
    "所在分区": "Group",
    "对外依赖": "Outgoing dependencies",
    "被其他模块依赖": "Incoming dependencies",
    "公开接口": "Public interfaces",
    "这些关系来自冻结代码中的静态 import，不证明运行时一定执行。": "These relationships come from static imports in fixed source; they do not prove runtime execution.",
    "返回分区说明": "Back to group explanation",
    "这一步对应多个静态分区；请选择一个实现分区继续查看。": "This step maps to several static groups. Select one to continue.",
    "这是系统外部的人工决定，不映射为代码分区。": "This is a human decision outside the system and does not map to a code group.",
    "这是外部输入或状态，不映射为单一代码分区。": "This is external input or state and does not map to a single code group.",
    "系统全景": "System overview",
    "从工作流进入实现": "From workflow to implementation",
    "在左侧图中点击有“点击展开”提示的工作步骤，静态实现会直接在同一张图中展开。": "Select a workflow step marked 'expand' to reveal its static implementation in the same map.",
    "系统分区": "System groups",
    "完整模块": "All modules",
    "静态关系": "Static relationships",
    "本次涉及分区": "Groups involved in this change",
    "当前实现子域": "Current implementation subdomain",
    "所属分区": "Parent group",
    "包含模块": "Modules",
    "对外入口": "External interfaces",
    "本次变化": "Changed modules",
    "分组依据": "Grouping source",
    "目标配置规则": "Target-profile rule",
    "自动候选": "Automatic candidate",
    "与其他实现子域的静态关系": "Static relationships with other subdomains",
    "每一项都聚合已有静态 import；它不代表运行时调用。": "Each item aggregates existing static imports; it is not a runtime call.",
    "当前没有跨实现子域的静态 import。": "There are no cross-subdomain static imports in this snapshot.",
    "当前静态实现分区": "Current static implementation group",
    "模块": "Modules",
    "内部关系": "Internal relationships",
    "流入分区": "Incoming groups",
    "流出分区": "Outgoing groups",
    "分区来源": "Group source",
    "待人工归类": "Needs human classification",
    "目标配置": "Target profile",
    "收起当前实现": "Collapse current implementation",
    "当前分区的全部静态关系": "All static relationships for this group",
    "全部分区关系": "All group relationships",
    "没有找到跨分区静态关系。": "No cross-group static relationships were found.",
    "逐层查看": "Inspect layer by layer",
    "返回分区关系图": "Back to group relationship map",
    "实现子域": "Implementation subdomain",
    "请先选择": "Select one first",
    "技术模块（可选）": "Technical modules (optional)",
    "已经展开": "Expanded",
    "默认收起": "Collapsed by default",
    "实现子域优先按目标配置规则匹配；未命中的模块会明确归入“其他”。子域关系只汇总已有静态 import，不代表运行时先后顺序。": "Implementation subdomains prefer target-profile rules. Unmatched modules are explicitly grouped as 'Other'. Their relationships summarize static imports, not runtime order.",
    "第 2 层 · 实现子域图": "Layer 2 · implementation subdomains",
    "每张卡是一个可审计的源码子域；箭头文字汇总子域之间已有的静态 import，而不是运行时调用。": "Each card is an auditable source subdomain. Arrow labels summarize static imports between subdomains, not runtime calls.",
    "目标配置优先": "Target profile first",
    "第 2 层 · 当前子区域": "Layer 2 · current subdomain",
    "换一个子区域": "Choose another subdomain",
    "本次涉及": "Involved in this change",
    "收起技术模块": "Collapse technical modules",
    "展开技术模块（可选）": "Expand technical modules (optional)",
    "技术模块": "Technical modules",
    "这个视图没有可显示的已验证节点。": "This view has no validated nodes to display.",
    "没有被折叠的代码关联位置。": "No code-relationship locations are folded.",
    "收起这一层": "Collapse this layer",
    "这里先按证据类型分组；再次点击才显示具体技术 ID。": "Items are grouped by evidence type first. Select again to reveal technical IDs.",
    "返回分组": "Back to groups",
    "全部收起": "Collapse all",
    "点击变化图中的节点，即可查看它原来负责什么、这次怎样变以及证据边界。": "Select a node in the change map to see its previous responsibility, the change, and the evidence boundary.",
    "它原来负责什么": "What it was responsible for",
    "这次怎样变了": "How it changed",
    "谁可能直接受到影响": "Who may be directly affected",
    "证据能证明到哪里": "How far the evidence goes",
    "哪里仍不清楚": "What remains unclear",
    "恢复完整关系": "Restore all relationships",
    "只看这条关联": "Focus on this relationship",
    "查看依据": "View evidence",
    "以下内容是上面结论的依据，不是另一份 AI 总结。页面只读取冻结样本的派生数据。": "The following is evidence for the conclusions above, not another AI summary. This page reads only derived data from the fixed sample.",
    "变化文件": "Changed files",
    "结构基线": "Structure baseline",
    "图中节点": "Displayed nodes",
    "结构边": "Structure edges",
    "明确折叠": "Explicitly folded",
    "完整系统模块": "All system modules",
    "完整静态关系": "All static relationships",
    "当前节点": "Current node",
    "全部已校验结论": "All validated conclusions",
    "已证实": "Verified",
    "有依据的推断": "Evidence-supported inference",
    "尚不清楚": "Unknown",
    "架构分析限制": "Architecture-analysis limitations",
    "本报告界面可切换中英文；项目说明、任务原话、技术证据和仅提供单语的解释正文保留来源语言。": "The report interface can switch between Chinese and English. Project descriptions, task quotations, technical evidence, and explanation text supplied in one language remain in their source language."
  });

  const PATTERNS = Object.freeze([
    [/^目标配置声明的产品\/流程架构 · (.+)$/, value => `Product/workflow architecture declared by target configuration · ${value}`],
    [/^(.+)。这是受支持代码的静态结构快照，不等于完整运行时架构；动态注入、数据库、网络调用和部署关系仍需独立证据。$/, value => `${value}. This is a static snapshot of supported code, not a complete runtime architecture. Dynamic injection, databases, network calls and deployment relationships require independent evidence.`],
    [/^(\d+) 个$/, value => `${value}`],
    [/^(\d+) 模块$/, value => `${value} modules`],
    [/^中文标签来源：(.+)$/, value => `Label source: ${value}`],
    [/^路径：(.+)$/, value => `Paths: ${value === "无" ? "None" : value}`],
    [/^接口：(.+)$/, value => `Interfaces: ${value === "无" ? "None" : value}`],
    [/^证据引用：(.+)$/, value => `Evidence references: ${value === "无" ? "None" : value}`],
    [/^证据：(.+)$/, value => `Evidence: ${value === "无" ? "None" : value}`],
    [/^限制：(.+)$/, value => `Limitations: ${value === "无" ? "None" : value}`],
    [/^最小检查：(.+)$/, value => `Minimum check: ${value}`],
    [/^其他(.+)模块$/, value => `Other ${value} modules`],
    [/^先从 (\d+) 个实现子域理解结构；只有需要核对时，才展开具体源码模块。$/, value => `Start with ${value} implementation areas; expand source modules only when needed.`],
    [/^以下是核对源码时才需要看的技术层。当前显示 (\d+) \/ (\d+)。$/, (shown, total) => `Technical details for source inspection. Showing ${shown} / ${total}.`],
    [/^按当前工作图，这个阶段从“(.+)”推进到“(.+)”。$/, (first, last) => `In this workflow, this stage goes from ${first} to ${last}.`],
    [/^本次修改定位在这个阶段中的“(.+)”。$/, value => `The change is located in this stage: ${value}.`],
    [/^本次修改定位在“(.+)”这项能力。$/, value => `The change is located in the “${value}” capability.`],
    [/^本次修改定位在当前步骤。(.*)$/, value => `The change is located in this step. ${value}`],
    [/^已定位到“(.+)”$/, value => `Located: ${value}`],
    [/^涉及内部：(.+)$/, value => `Internal area: ${value}`],
    [/^仍有 (\d+) 项需要确认$/, value => `${value} items still need confirmation`],
    [/^整体结构 (\d+) 区$/, value => `${value} architecture groups`],
    [/^从固定版本的代码位置看，这次变化最可能对应“(.+)”这一步；确定性检查尚未解释具体行为，实际效果也还没运行验证。$/, value => `Fixed source locations suggest that this change most likely belongs to “${value}”. The deterministic checks have not explained the exact behavior, and the actual result has not been run or verified.`],
    [/^从固定版本的代码位置看，这次变化最可能对应“(.+)”这一步；还没有运行软件验证实际效果。$/, value => `Fixed source locations suggest that this change most likely belongs to “${value}”. The software has not been run to verify the actual result.`],
    [/^在“(.+)”完成一次正常操作，确认仍能得到预期结果$/, value => `Complete one normal operation in “${value}” and confirm that it still produces the expected result`],
    [/^从“(.+)”到“(.+)”，包含 (\d+) 个详细步骤。$/, (first, last, count) => `From “${first}” to “${last}”, this stage contains ${count} detailed steps.`],
    [/^先用四个阶段理解 (.+)$/, value => `Understand ${value} in four stages`],
    [/^先看 (.+) 能做什么$/, value => `See what ${value} can do`],
    [/^四步看懂这个软件$/, () => "Understand this software in four steps"],
    [/^主要能力（没有先后顺序）$/, () => "Main capabilities (no fixed order)"],
    [/^(.+) 怎样从输入走到结果$/, value => `How ${value} turns input into results`],
    [/^(.+) 包含哪些主要能力$/, value => `Main capabilities in ${value}`],
    [/^先看四个阶段，再展开项目说明中的详细步骤和对应证据状态。$/, () => "Start with four stages, then expand the detailed project-declared steps and their evidence status."],
    [/^在软件流程中查看：(.+)$/, value => `View in the software workflow: ${value}`],
    [/^在软件能力图中查看：(.+)$/, value => `View in the software capability map: ${value}`],
    [/^已定位到“(.+)”$/, value => `Located “${value}”`],
    [/^四步总览 · 已展开「(.+)」$/, value => `Four-step overview · expanded “${value}”`],
    [/^能力全景 · 已展开「(.+)」$/, value => `Capability overview · expanded “${value}”`],
    [/^这里包含 (\d+) 个详细步骤$/, value => `This stage contains ${value} detailed steps`],
    [/^已识别 (\d+) 项内部职责$/, value => `${value} internal responsibilities identified`],
    [/^(\d+) 个步骤$/, value => `${value} steps`],
    [/^(\d+) 项依据$/, value => `${value} evidence item${value === "1" ? "" : "s"}`],
    [/^(\d+) 个系统分区$/, value => `${value} system groups`],
    [/^(\d+) 个模块$/, value => `${value} modules`],
    [/^(\d+) 条静态关系$/, value => `${value} static relationships`],
    [/^(\d+) 个待归类$/, value => `${value} unclassified`],
    [/^本次变化 (\d+)$/, value => `${value} changed`],
    [/^本次涉及 (\d+)$/, value => `${value} involved`],
    [/^入 (\d+) \/ 出 (\d+)$/, (left, right) => `in ${left} / out ${right}`],
    [/^(\d+) 条$/, value => `${value}`],
    [/^(\d+) 条静态 import$/, value => `${value} static imports`],
    [/^(\d+) 条可追溯静态依赖$/, value => `${value} traceable static dependencies`],
    [/^还有 (\d+) 个静态关联位置$/, value => `${value} more static relationship locations`],
    [/^另有 (\d+) 条已确认代码关联，完整关系保留在技术依据和 JSON 中。$/, value => `${value} additional confirmed code relationships remain available in the technical evidence and JSON.`],
    [/^已切换到(.+)$/, value => `Switched to ${value}`],
    [/^再显示 (\d+) 个模块$/, value => `Show ${value} more modules`],
    [/^正在查看(.+)$/, value => `Viewing ${value}`],
    [/^已选择(.+)$/, value => `Selected ${value}`],
    [/^点击展开：(.+)$/, value => `Expand: ${value}`],
    [/^对应实现：(.+)$/, value => `Implementation: ${value}`],
    [/^按需核对 (\d+) 个技术模块$/, value => `Inspect ${value} technical modules on demand`],
    [/^(.+)由哪些实现部分组成$/, value => `Which implementation parts make up ${value}`],
    [/^(.+) · 技术模块$/, value => `${value} · technical modules`],
    [/^(.+) · 逐层查看$/, value => `${value} · inspect layer by layer`],
    [/^(.+)的详细过程$/, value => `${value} details`],
    [/^(.+)的能力依据$/, value => `${value} capability evidence`],
    [/^当前显示 (\d+) \/ (\d+)。$/, (shown, total) => `Showing ${shown} / ${total}.`]
  ]);

  function normalizedLocale(value) {
    return String(value || "").toLowerCase().startsWith("zh") ? "zh-CN" : "en";
  }

  function hashLocale() {
    const marker = String(location.hash || "").replace(/^#/, "");
    if (!marker.startsWith(HASH_PREFIX)) return null;
    const value = decodeURIComponent(marker.slice(HASH_PREFIX.length));
    return SUPPORTED.includes(value) ? value : null;
  }

  function storedLocale() {
    try {
      const value = localStorage.getItem(STORAGE_KEY);
      return SUPPORTED.includes(value) ? value : null;
    } catch (_) {
      return null;
    }
  }

  function preferredLocale() {
    return hashLocale() || storedLocale() || normalizedLocale((navigator.languages || [navigator.language])[0]);
  }

  const locale = preferredLocale();

  function translateCore(value) {
    if (locale !== "en" || typeof value !== "string" || !value) return value;
    if (Object.prototype.hasOwnProperty.call(EN, value)) return EN[value];
    for (const [pattern, render] of PATTERNS) {
      const match = value.match(pattern);
      if (match) return render(...match.slice(1));
    }
    return value;
  }

  function translateText(value) {
    if (locale !== "en" || typeof value !== "string") return value;
    const match = value.match(/^(\s*)(.*?)(\s*)$/s);
    return `${match[1]}${translateCore(match[2])}${match[3]}`;
  }

  function translateElement(element) {
    if (element.closest?.("script, style, [data-preserve-language='true']")) return;
    for (const name of ["aria-label", "title", "placeholder"]) {
      if (element.hasAttribute?.(name)) {
        const before = element.getAttribute(name);
        const after = translateCore(before);
        if (after !== before) element.setAttribute(name, after);
      }
    }
  }

  function translateTree(root) {
    if (locale !== "en" || !root) return;
    if (root.nodeType === Node.TEXT_NODE) {
      if (root.parentElement?.closest?.("script, style, [data-preserve-language='true']")) return;
      const after = translateText(root.nodeValue);
      if (after !== root.nodeValue) root.nodeValue = after;
      return;
    }
    if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_NODE) return;
    if (root.nodeType === Node.ELEMENT_NODE) translateElement(root);
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    let node;
    while ((node = walker.nextNode())) {
      if (node.nodeType === Node.TEXT_NODE) {
        if (node.parentElement?.closest?.("script, style, [data-preserve-language='true']")) continue;
        const after = translateText(node.nodeValue);
        if (after !== node.nodeValue) node.nodeValue = after;
      } else {
        translateElement(node);
      }
    }
  }

  function setLocale(next) {
    if (!SUPPORTED.includes(next) || next === locale) return;
    try { localStorage.setItem(STORAGE_KEY, next); } catch (_) {}
    const nextHash = `#${HASH_PREFIX}${encodeURIComponent(next)}`;
    if (location.hash !== nextHash) {
      try {
        history.replaceState(null, "", nextHash);
      } catch (_) {
        location.hash = nextHash;
      }
    }
    location.reload();
  }

  function bootstrap() {
    document.documentElement.lang = locale;
    document.documentElement.dataset.locale = locale;
    document.title = locale === "en" ? "PlainChange review" : "PlainChange 变化说明";
    const control = document.getElementById("language-switch");
    if (control) {
      control.querySelectorAll("button[data-locale]").forEach(button => {
        const active = button.dataset.locale === locale;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", String(active));
        button.addEventListener("click", () => setLocale(button.dataset.locale));
      });
    }
    translateTree(document.body);
    const observer = new MutationObserver(records => {
      records.forEach(record => {
        if (record.type === "attributes") translateElement(record.target);
        record.addedNodes.forEach(translateTree);
      });
    });
    observer.observe(document.body, {subtree: true, childList: true, attributes: true, attributeFilter: ["aria-label", "title", "placeholder"]});
    document.documentElement.dataset.i18nReady = "true";
  }

  window.PlainChangeI18n = Object.freeze({SUPPORTED, locale, setLocale, translateText});
  bootstrap();
})();
