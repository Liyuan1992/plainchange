(() => {
  "use strict";

  const data = JSON.parse(document.getElementById("review-data").textContent);
  const architecture = data.system_architecture;
  const architectureGroups = new Map(
    (architecture?.groups || []).map((group) => [group.group_id, group]),
  );
  const architectureGroupEdges = new Map(
    (architecture?.group_edges || []).map((edge) => [edge.group_edge_id, edge]),
  );
  const architectureNodes = new Map(
    (architecture?.nodes || []).map((node) => [node.node_id, node]),
  );
  const architectureEdges = new Map(
    (architecture?.edges || []).map((edge) => [edge.edge_id, edge]),
  );
  const state = {
    page: "change",
    pageScroll: {change: 0, architecture: 0},
    summaryContextOpen: false,
    view: "after",
    selectedId: data.default_node_id,
    branchLevel: 0,
    branchGroup: null,
    evidenceOpen: false,
    focusPath: false,
    architectureSelectedGroup: null,
    architectureSelectedRelation: null,
    architectureSelectedNode: null,
    architectureSelectedArea: null,
    architectureModuleDetailsOpen: false,
    architectureDepth: "overview",
    architectureModuleLimit: 18,
  };

  const byId = (id) => document.getElementById(id);
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };
  const makeSvg = (tag, className) => {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    if (className) node.setAttribute("class", className);
    return node;
  };
  const clear = (node) => {
    while (node.firstChild) node.removeChild(node.firstChild);
  };
  const append = (parent, ...children) => {
    children.filter(Boolean).forEach((child) => parent.appendChild(child));
    return parent;
  };
  const truthClass = (value) => ["verified", "inference", "context", "unknown"].includes(value) ? value : "unknown";
  const nodeIcon = (status) => ({added: "+", removed: "−", modified: "↻", impacted: "↗", unchanged_context: "○"}[status] || "○");

  function showToast(message) {
    const toast = byId("toast");
    toast.textContent = message;
    toast.hidden = false;
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => { toast.hidden = true; }, 2200);
  }

  function renderHeader() {
    byId("eyebrow").textContent = data.header.eyebrow;
    byId("page-title").textContent = data.header.title;
    byId("subtitle").textContent = data.header.subtitle;
    byId("scope-note").textContent = data.header.scope_note;
    byId("review-identity").textContent = `review ${String(data.review_identity).slice(0, 12)}`;
    const host = byId("top-status");
    clear(host);
    data.header.statuses.forEach((status) => {
      host.appendChild(make("span", `chip ${status.tone}`, status.label));
    });
  }

  function renderSummary() {
    const host = byId("summary-grid");
    clear(host);
    data.summary.forEach((item) => {
      const context = item.task_context;
      const contextOpen = item.id === "summary.why" && state.summaryContextOpen;
      const card = make("article", `summary-card${contextOpen ? " context-open" : ""}`);
      card.dataset.tone = truthClass(item.truth_state);
      const head = make("div", "summary-head");
      append(
        head,
        make("span", "summary-icon", item.icon),
        make("span", `truth ${truthClass(item.truth_state)}`, item.truth_label),
      );
      append(card, head, make("h2", "", item.question));
      if (item.items.length > 1) {
        const list = make("ul", "summary-items");
        item.items.forEach((entry) => list.appendChild(make("li", "", entry.text)));
        card.appendChild(list);
      } else {
        card.appendChild(make("p", "summary-copy", item.items.length ? item.items[0].text : item.text));
      }
      if (item.next_check) {
        card.appendChild(make("p", "summary-next", `最小检查：${item.next_check}`));
      }
      if (context?.entries?.length) {
        const actions = make("div", "summary-context-actions");
        const toggle = make(
          "button",
          "secondary-button summary-context-button",
          contextOpen ? "收起任务线索" : context.action_label,
        );
        toggle.type = "button";
        toggle.dataset.summaryContext = item.id;
        toggle.setAttribute("aria-expanded", String(contextOpen));
        toggle.setAttribute("aria-controls", "summary-why-context");
        toggle.addEventListener("click", () => {
          state.summaryContextOpen = !state.summaryContextOpen;
          renderSummary();
          document.querySelector('[data-summary-context="summary.why"]')?.focus();
        });
        append(actions, toggle, make("span", "summary-context-cost", context.action_cost));
        card.appendChild(actions);
        const panel = make("section", "summary-context-panel");
        panel.id = "summary-why-context";
        panel.hidden = !contextOpen;
        panel.setAttribute("aria-label", "已有任务线索");
        context.entries.forEach((entry) => {
          const row = make("article", `summary-context-entry ${entry.role}`);
          append(
            row,
            append(
              make("div", "summary-context-entry-head"),
              make("strong", "", entry.role_label),
              make("span", "", entry.source_label),
            ),
            make("p", "", entry.text),
            entry.warning ? make("small", "summary-context-warning", entry.warning) : null,
          );
          panel.appendChild(row);
        });
        panel.appendChild(make("p", "summary-context-rule", "判断顺序：用户明确提出 → AI 给出解释 → 用户是否确认。三种来源不能混为一谈。"));
        card.appendChild(panel);
      }
      host.appendChild(card);
    });
  }

  function switchPage(nextPage, announce = true) {
    if (nextPage === "architecture" && !architecture) {
      showToast("当前样本没有整体架构快照");
      return;
    }
    state.pageScroll[state.page] = window.scrollY;
    state.page = nextPage;
    if (nextPage !== "change") state.summaryContextOpen = false;
    byId("change-page").hidden = nextPage !== "change";
    byId("architecture-page").hidden = nextPage !== "architecture";
    document.querySelectorAll("[data-page]").forEach((button) => {
      button.setAttribute("aria-selected", String(button.dataset.page === nextPage));
      button.tabIndex = button.dataset.page === nextPage ? 0 : -1;
    });
    if (nextPage === "architecture") {
      renderArchitecture();
    }
    window.requestAnimationFrame(() => {
      window.scrollTo({top: state.pageScroll[nextPage] || 0, behavior: "auto"});
      if (nextPage === "architecture") drawArchitectureLinks();
    });
    if (announce) showToast(nextPage === "architecture" ? "已切换到整体架构" : "已切换到变化解读");
  }

  function architectureGroupLabel(groupId) {
    return architectureGroups.get(groupId)?.label || "待归类";
  }

  function architectureNodeLabel(node) {
    return data.node_details?.[node.node_id]?.label
      || node.responsibilities?.[0]
      || node.label
      || "模块职责尚未确认";
  }

  function changedNodeSet() {
    if (!architecture) return new Set();
    return new Set([
      ...architecture.change_overlay.added,
      ...architecture.change_overlay.modified,
      ...architecture.change_overlay.removed,
    ]);
  }

  const architectureModuleAreaRules = [
    {
      id: "web-chat",
      order: 2,
      prefixes: ["src/digital_self/web/static/modules/chat/"],
      label: "聊天与对话界面",
      description: "聊天页面中的显示与操作模块，按源码目录归在一起。",
    },
    {
      id: "web-ui",
      order: 1,
      prefixes: ["src/digital_self/web/static/"],
      label: "网页功能界面",
      description: "网页中可见的页面与功能模块，按前端目录归在一起。",
    },
    {
      id: "desktop-browser",
      order: 3,
      prefixes: ["desktop/", "browser_extension/"],
      label: "桌面与浏览器入口",
      description: "桌面外壳和浏览器扩展中的入口模块。",
    },
    {
      id: "cli",
      order: 4,
      prefixes: ["src/digital_self/cli/"],
      label: "命令行入口",
      description: "在终端中使用的命令入口与公共辅助模块。",
    },
    {
      id: "voice-vtuber",
      order: 5,
      prefixes: ["src/digital_self/voice/", "src/digital_self/vtuber/"],
      label: "语音与数字人",
      description: "语音交互和数字人接入相关模块。",
    },
    {
      id: "web-api",
      order: 6,
      prefixes: ["src/digital_self/web/"],
      label: "网页背后的服务",
      description: "为网页、桌面和浏览器提供数据与操作能力的后台服务。",
    },
    {
      id: "memory-review",
      order: 1,
      prefixes: ["src/digital_self/memory/review/", "src/digital_self/memory/reviewed_write/"],
      label: "记忆审核与写入",
      description: "记忆进入长期存储前后的审核与受控写入模块。",
    },
    {
      id: "memory",
      order: 2,
      prefixes: ["src/digital_self/memory/", "src/digital_self/knowledge/", "src/digital_self/learning/"],
      label: "记忆与知识服务",
      description: "记忆检索、整理、迁移和知识读取相关模块。",
    },
    {
      id: "agent-runtime",
      order: 1,
      prefixes: ["src/digital_self/agents/", "src/digital_self/core/", "src/digital_self/kernel/", "src/digital_self/worker/", "src/digital_self/session/", "src/digital_self/pipeline/", "src/digital_self/workflow/"],
      label: "智能体运行与任务执行",
      description: "智能体、会话和任务运行生命周期中的模块。",
    },
    {
      id: "capabilities",
      order: 1,
      prefixes: ["src/digital_self/skills/", "src/digital_self/tools/", "src/digital_self/control/", "src/digital_self/llm/"],
      label: "能力、工具与模型接入",
      description: "可调用能力、工具执行和模型连接相关模块。",
    },
    {
      id: "context-governance",
      order: 1,
      prefixes: ["src/digital_self/context/", "src/digital_self/autonomy/", "src/digital_self/requirements/"],
      label: "上下文与自主控制",
      description: "上下文组织、边界约束和自主任务控制相关模块。",
    },
    {
      id: "work-coordination",
      order: 1,
      prefixes: ["src/digital_self/work_inbox/", "src/digital_self/product_workflows/"],
      label: "工作与项目协作",
      description: "工作收件箱、项目流程和协作结果相关模块。",
    },
    {
      id: "data-foundation",
      order: 1,
      prefixes: ["src/digital_self/data/", "src/digital_self/storage/", "src/digital_self/config/"],
      label: "数据与配置基础",
      description: "数据访问、存储和配置基础相关模块。",
    },
    {
      id: "integrations",
      order: 7,
      prefixes: ["src/digital_self/adapters/", "src/digital_self/integrations/"],
      label: "外部接入适配",
      description: "连接外部应用或既有接口的适配模块。",
    },
    {
      id: "tests",
      order: 1,
      prefixes: ["tests/"],
      label: "测试与验证",
      description: "用于验证系统行为和边界的测试模块。",
    },
    {
      id: "engineering",
      order: 2,
      prefixes: ["scripts/", "packaging/"],
      label: "工程脚本与交付",
      description: "构建、检查、打包和交付辅助模块。",
    },
  ];

  function architectureModuleAreas(group, nodes) {
    const involved = new Set([
      ...architecture.change_overlay.added,
      ...architecture.change_overlay.modified,
      ...architecture.change_overlay.removed,
      ...architecture.change_overlay.impacted,
    ]);
    const areas = new Map();
    nodes.forEach((node) => {
      const path = String(node.owned_paths?.[0] || "").replaceAll("\\", "/").toLowerCase();
      const rule = architectureModuleAreaRules.find((candidate) =>
        candidate.prefixes.some((prefix) => path.startsWith(prefix))
      ) || {
        id: `${group.group_id}-other`,
        order: 99,
        label: group.group_id === "entry_experience" ? "其他用户入口" : `其他${group.label}模块`,
        description: "未归入前述目录的模块，集中保留在这个阅读分组中。",
      };
      if (!areas.has(rule.id)) {
        areas.set(rule.id, {
          ...rule,
          nodes: [],
          interfaceCount: 0,
          involvedCount: 0,
        });
      }
      const area = areas.get(rule.id);
      area.nodes.push(node);
      area.interfaceCount += node.interfaces?.length || 0;
      if (involved.has(node.node_id)) area.involvedCount += 1;
    });
    return [...areas.values()]
      .map((area) => ({...area, nodes: area.nodes.sort((left, right) => left.node_id.localeCompare(right.node_id))}))
      .sort((left, right) => left.order - right.order || right.nodes.length - left.nodes.length || left.id.localeCompare(right.id));
  }

  function renderArchitectureHeader() {
    const coverage = architecture.coverage;
    byId("architecture-description").textContent = "完整覆盖当前冻结版本中成功解析的受支持代码；变化分区已高亮，点击分区可继续查看模块。";
    const stats = byId("architecture-stats");
    clear(stats);
    [
      `${coverage.group_count} 个系统分区`,
      `${coverage.node_count} 个模块`,
      `${coverage.edge_count} 条静态关系`,
      `${coverage.unclassified_node_count} 个待归类`,
    ].forEach((label, index) => {
      stats.appendChild(make("span", `chip ${index === 3 && coverage.unclassified_node_count ? "warn" : "info"}`, label));
    });
    byId("architecture-scope").textContent = `${architecture.status_label}。这是受支持代码的静态结构快照，不等于完整运行时架构；动态注入、数据库、网络调用和部署关系仍需独立证据。`;
  }

  function architectureGroupButton(group) {
    const button = make("button", `system-group ${group.lane}${group.changed_count ? " changed" : ""}`);
    button.type = "button";
    button.dataset.groupId = group.group_id;
    button.setAttribute("aria-selected", String(state.architectureSelectedGroup === group.group_id));
    if (state.architectureSelectedGroup) {
      const selectedEdge = architectureGroupEdges.get(state.architectureSelectedRelation);
      const isSelected = group.group_id === state.architectureSelectedGroup;
      const isRelated = architecture.group_edges.some((edge) =>
        (edge.source_group_id === state.architectureSelectedGroup && edge.target_group_id === group.group_id)
        || (edge.target_group_id === state.architectureSelectedGroup && edge.source_group_id === group.group_id)
      );
      const isOnSelectedRelation = selectedEdge
        && (selectedEdge.source_group_id === group.group_id || selectedEdge.target_group_id === group.group_id);
      if (isRelated || isOnSelectedRelation) button.classList.add("is-related");
      if (selectedEdge ? !isOnSelectedRelation : !isSelected && !isRelated) {
        button.classList.add("is-dimmed");
      }
    }
    append(
      button,
      make("span", "system-group-title", group.label),
      make("span", "system-group-copy", group.responsibility),
    );
    const meta = make("span", "system-group-meta");
    append(
      meta,
      make("span", "", `${group.module_count} 个模块`),
      make("span", "", `${group.incoming_relation_count + group.outgoing_relation_count} 组关系`),
      group.changed_count ? make("span", "", `本次变化 ${group.changed_count}`) : null,
    );
    button.appendChild(meta);
    button.addEventListener("click", () => {
      state.architectureSelectedGroup = group.group_id;
      state.architectureSelectedRelation = null;
      state.architectureSelectedNode = null;
      state.architectureSelectedArea = null;
      state.architectureModuleDetailsOpen = false;
      state.architectureDepth = "overview";
      state.architectureModuleLimit = 18;
      renderArchitecture();
      showToast(`正在查看${group.label}`);
    });
    return button;
  }

  function renderArchitectureGroups() {
    const host = byId("architecture-groups");
    clear(host);
    const canvas = byId("architecture-canvas");
    const selectedGroup = architectureGroups.get(state.architectureSelectedGroup);
    host.classList.toggle("is-focus-view", Boolean(selectedGroup));
    canvas.classList.toggle("focus-mode", Boolean(selectedGroup));
    if (!selectedGroup) {
      architecture.groups.forEach((group) => host.appendChild(architectureGroupButton(group)));
      return;
    }

    const relations = architecture.group_edges
      .filter((edge) => edge.source_group_id === selectedGroup.group_id || edge.target_group_id === selectedGroup.group_id);
    const incoming = relations
      .filter((edge) => edge.target_group_id === selectedGroup.group_id)
      .sort((left, right) => right.edge_count - left.edge_count);
    const outgoing = relations
      .filter((edge) => edge.source_group_id === selectedGroup.group_id)
      .sort((left, right) => right.edge_count - left.edge_count);

    function focusColumn(title, direction, edges) {
      const column = make("section", `architecture-focus-column ${direction}`);
      append(
        column,
        make("h4", "", title),
        make("p", "", direction === "incoming" ? "这些分区使用了当前分区" : "当前分区使用了这些分区"),
      );
      const list = make("div", "architecture-focus-list");
      edges.forEach((edge) => {
        const otherGroupId = direction === "incoming" ? edge.source_group_id : edge.target_group_id;
        const button = make("button", `architecture-focus-relation ${direction}`);
        button.type = "button";
        button.dataset.focusEdgeId = edge.group_edge_id;
        button.dataset.focusDirection = direction;
        button.setAttribute("aria-pressed", String(state.architectureSelectedRelation === edge.group_edge_id));
        if (state.architectureSelectedRelation && state.architectureSelectedRelation !== edge.group_edge_id) {
          button.classList.add("is-dimmed");
        }
        append(
          button,
          make("span", "focus-relation-name", architectureGroupLabel(otherGroupId)),
          make("span", "focus-relation-count", `${edge.edge_count} 条`),
        );
        button.addEventListener("click", () => {
          state.architectureSelectedRelation = state.architectureSelectedRelation === edge.group_edge_id
            ? null
            : edge.group_edge_id;
          renderArchitecture();
          showToast(state.architectureSelectedRelation ? `已单独显示与${architectureGroupLabel(otherGroupId)}的关系` : "已恢复当前分区全部关系");
        });
        list.appendChild(button);
      });
      column.appendChild(list);
      return column;
    }

    const focus = make("div", "architecture-focus-map");
    const center = make("section", `architecture-focus-center ${selectedGroup.changed_count ? "changed" : ""}`);
    center.dataset.focusCenter = selectedGroup.group_id;
    append(
      center,
      make("span", "eyebrow", "当前分区"),
      make("h3", "", selectedGroup.label),
      make("p", "", selectedGroup.responsibility),
      make("span", "architecture-focus-hint", "点击两侧任一关系，可只看这一条线"),
    );
    append(
      focus,
      focusColumn(`谁依赖它 · ${incoming.length} 个`, "incoming", incoming),
      center,
      focusColumn(`它依赖谁 · ${outgoing.length} 个`, "outgoing", outgoing),
    );
    host.appendChild(focus);
  }

  function architectureVisibleEdges() {
    const edges = [...architecture.group_edges];
    if (state.architectureSelectedRelation) {
      const selected = architectureGroupEdges.get(state.architectureSelectedRelation);
      return selected ? [selected] : [];
    }
    if (state.architectureSelectedGroup) {
      return edges.filter((edge) =>
        edge.source_group_id === state.architectureSelectedGroup
        || edge.target_group_id === state.architectureSelectedGroup
      );
    }
    return edges
      .filter((edge) =>
        architectureGroups.get(edge.source_group_id)?.lane === "main"
        && architectureGroups.get(edge.target_group_id)?.lane === "main"
      )
      .sort((left, right) => right.edge_count - left.edge_count)
      .slice(0, 6);
  }

  function architectureEdgeDirection(edge) {
    if (!state.architectureSelectedGroup) return "overview";
    return edge.source_group_id === state.architectureSelectedGroup ? "outgoing" : "incoming";
  }

  function architectureSide(rect, other) {
    const dx = other.centerX - rect.centerX;
    const dy = other.centerY - rect.centerY;
    return Math.abs(dx / rect.width) >= Math.abs(dy / rect.height)
      ? (dx >= 0 ? "right" : "left")
      : (dy >= 0 ? "bottom" : "top");
  }

  function architecturePort(rect, side, index, count) {
    const ratio = (index + 1) / (count + 1);
    if (side === "left" || side === "right") {
      return {
        x: side === "left" ? rect.left : rect.right,
        y: rect.top + rect.height * ratio,
      };
    }
    return {
      x: rect.left + rect.width * ratio,
      y: side === "top" ? rect.top : rect.bottom,
    };
  }

  function architectureDirectionVector(side) {
    return {
      left: {x: -1, y: 0},
      right: {x: 1, y: 0},
      top: {x: 0, y: -1},
      bottom: {x: 0, y: 1},
    }[side];
  }

  function addArchitectureMarker(defs, id, tone) {
    const marker = makeSvg("marker");
    marker.setAttribute("id", id);
    marker.setAttribute("viewBox", "0 0 10 10");
    marker.setAttribute("refX", "9");
    marker.setAttribute("refY", "5");
    marker.setAttribute("markerWidth", "7");
    marker.setAttribute("markerHeight", "7");
    marker.setAttribute("orient", "auto");
    const arrow = makeSvg("path", `architecture-arrow-fill ${tone}`);
    arrow.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
    marker.appendChild(arrow);
    defs.appendChild(marker);
  }

  function drawArchitectureLinks() {
    const svg = byId("architecture-links");
    clear(svg);
    if (!architecture || state.page !== "architecture" || window.innerWidth <= 720) return;
    const canvas = byId("architecture-canvas");
    const canvasRect = canvas.getBoundingClientRect();
    const width = Math.max(canvas.scrollWidth, canvas.clientWidth);
    const height = Math.max(canvas.scrollHeight, canvas.clientHeight);
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("width", String(width));
    svg.setAttribute("height", String(height));

    const defs = makeSvg("defs");
    addArchitectureMarker(defs, "architecture-arrow-overview", "overview");
    addArchitectureMarker(defs, "architecture-arrow-outgoing", "outgoing");
    addArchitectureMarker(defs, "architecture-arrow-incoming", "incoming");
    svg.appendChild(defs);

    if (state.architectureSelectedGroup) {
      const centerNode = canvas.querySelector("[data-focus-center]");
      if (!centerNode) return;
      const centerRaw = centerNode.getBoundingClientRect();
      const centerRect = {
        left: centerRaw.left - canvasRect.left + canvas.scrollLeft,
        top: centerRaw.top - canvasRect.top + canvas.scrollTop,
        right: centerRaw.right - canvasRect.left + canvas.scrollLeft,
        bottom: centerRaw.bottom - canvasRect.top + canvas.scrollTop,
        width: centerRaw.width,
        height: centerRaw.height,
      };
      const visibleEdges = architectureVisibleEdges();
      const incoming = visibleEdges.filter((edge) => edge.target_group_id === state.architectureSelectedGroup);
      const outgoing = visibleEdges.filter((edge) => edge.source_group_id === state.architectureSelectedGroup);

      function focusRect(edge) {
        const node = canvas.querySelector(`[data-focus-edge-id="${edge.group_edge_id}"]`);
        if (!node) return null;
        const raw = node.getBoundingClientRect();
        return {
          left: raw.left - canvasRect.left + canvas.scrollLeft,
          top: raw.top - canvasRect.top + canvas.scrollTop,
          right: raw.right - canvasRect.left + canvas.scrollLeft,
          bottom: raw.bottom - canvasRect.top + canvas.scrollTop,
          centerY: raw.top - canvasRect.top + canvas.scrollTop + raw.height / 2,
        };
      }

      function drawFocusSide(edges, direction) {
        const prepared = edges.map((edge) => ({edge, rect: focusRect(edge)})).filter((item) => item.rect);
        prepared.sort((left, right) => left.rect.centerY - right.rect.centerY);
        prepared.forEach((item, index) => {
          const centerPort = architecturePort(
            centerRect,
            direction === "incoming" ? "left" : "right",
            index,
            prepared.length,
          );
          const start = direction === "incoming"
            ? {x: item.rect.right, y: item.rect.centerY}
            : centerPort;
          const end = direction === "incoming"
            ? centerPort
            : {x: item.rect.left, y: item.rect.centerY};
          const span = Math.max(32, Math.abs(end.x - start.x) * .45);
          const path = makeSvg(
            "path",
            `architecture-link ${direction}${state.architectureSelectedRelation === item.edge.group_edge_id ? " isolated" : ""}`,
          );
          path.dataset.groupEdgeId = item.edge.group_edge_id;
          path.setAttribute("d", `M ${start.x} ${start.y} C ${start.x + span} ${start.y}, ${end.x - span} ${end.y}, ${end.x} ${end.y}`);
          path.setAttribute("marker-end", `url(#architecture-arrow-${direction})`);
          svg.appendChild(path);
        });
      }

      drawFocusSide(incoming, "incoming");
      drawFocusSide(outgoing, "outgoing");
      return;
    }

    const changedGroups = new Set(architecture.change_overlay.group_ids);
    const visibleEdges = architectureVisibleEdges();
    const rects = new Map();
    architecture.groups.forEach((group) => {
      const node = canvas.querySelector(`[data-group-id="${group.group_id}"]`);
      if (!node) return;
      const raw = node.getBoundingClientRect();
      const left = raw.left - canvasRect.left + canvas.scrollLeft;
      const top = raw.top - canvasRect.top + canvas.scrollTop;
      rects.set(group.group_id, {
        left,
        top,
        right: left + raw.width,
        bottom: top + raw.height,
        width: raw.width,
        height: raw.height,
        centerX: left + raw.width / 2,
        centerY: top + raw.height / 2,
      });
    });
    const prepared = visibleEdges.map((edge) => {
      const sourceRect = rects.get(edge.source_group_id);
      const targetRect = rects.get(edge.target_group_id);
      if (!sourceRect || !targetRect) return null;
      return {
        edge,
        sourceRect,
        targetRect,
        sourceSide: architectureSide(sourceRect, targetRect),
        targetSide: architectureSide(targetRect, sourceRect),
      };
    }).filter(Boolean);
    const endpointBuckets = new Map();
    prepared.forEach((item) => {
      [
        {role: "source", groupId: item.edge.source_group_id, side: item.sourceSide, other: item.targetRect},
        {role: "target", groupId: item.edge.target_group_id, side: item.targetSide, other: item.sourceRect},
      ].forEach((endpoint) => {
        const key = `${endpoint.groupId}:${endpoint.side}`;
        if (!endpointBuckets.has(key)) endpointBuckets.set(key, []);
        endpointBuckets.get(key).push({item, ...endpoint});
      });
    });
    endpointBuckets.forEach((bucket) => {
      bucket.sort((left, right) =>
        (left.side === "top" || left.side === "bottom")
          ? left.other.centerX - right.other.centerX
          : left.other.centerY - right.other.centerY
      );
      bucket.forEach((endpoint, index) => {
        endpoint.item[`${endpoint.role}Port`] = architecturePort(
          rects.get(endpoint.groupId), endpoint.side, index, bucket.length,
        );
      });
    });

    prepared.forEach((item) => {
      const {edge, sourcePort: start, targetPort: end, sourceSide, targetSide} = item;
      const direction = architectureEdgeDirection(edge);
      const isolated = state.architectureSelectedRelation === edge.group_edge_id;
      const sourceVector = architectureDirectionVector(sourceSide);
      const targetVector = architectureDirectionVector(targetSide);
      const distance = Math.hypot(end.x - start.x, end.y - start.y);
      const controlDistance = Math.max(30, Math.min(92, distance * .28));
      const control1 = {
        x: start.x + sourceVector.x * controlDistance,
        y: start.y + sourceVector.y * controlDistance,
      };
      const control2 = {
        x: end.x + targetVector.x * controlDistance,
        y: end.y + targetVector.y * controlDistance,
      };
      const path = makeSvg(
        "path",
        `architecture-link ${direction}${isolated ? " isolated" : ""}${changedGroups.has(edge.source_group_id) || changedGroups.has(edge.target_group_id) ? " touches-change" : ""}`,
      );
      path.dataset.groupEdgeId = edge.group_edge_id;
      path.setAttribute("d", `M ${start.x} ${start.y} C ${control1.x} ${control1.y}, ${control2.x} ${control2.y}, ${end.x} ${end.y}`);
      path.setAttribute("marker-end", `url(#architecture-arrow-${direction})`);
      svg.appendChild(path);

      if (!state.architectureSelectedGroup) return;
      const labelX = (start.x + 3 * control1.x + 3 * control2.x + end.x) / 8;
      const labelY = (start.y + 3 * control1.y + 3 * control2.y + end.y) / 8;
      const labelText = `${edge.edge_count} 条`;
      const labelWidth = 22 + labelText.length * 7;
      const label = makeSvg("g", `architecture-link-label ${direction}`);
      label.dataset.groupEdgeId = edge.group_edge_id;
      const labelBackground = makeSvg("rect", "architecture-link-label-bg");
      labelBackground.setAttribute("x", String(labelX - labelWidth / 2));
      labelBackground.setAttribute("y", String(labelY - 11));
      labelBackground.setAttribute("width", String(labelWidth));
      labelBackground.setAttribute("height", "22");
      labelBackground.setAttribute("rx", "11");
      const labelValue = makeSvg("text", "architecture-link-label-text");
      labelValue.setAttribute("x", String(labelX));
      labelValue.setAttribute("y", String(labelY + 4));
      labelValue.setAttribute("text-anchor", "middle");
      labelValue.textContent = labelText;
      append(label, labelBackground, labelValue);
      svg.appendChild(label);
    });
  }

  function renderArchitectureDirectRelations(host, group) {
    const relations = architecture.group_edges
      .filter((edge) => edge.source_group_id === group.group_id || edge.target_group_id === group.group_id)
      .slice()
      .sort((left, right) => right.edge_count - left.edge_count);
    const panel = make("section", "architecture-direct-relations");
    append(
      panel,
      make("h4", "", "直接关系 · 点击可单独追踪"),
      make("p", "architecture-relation-help", "箭头表示静态 import 方向，不代表运行先后。"),
    );
    const legend = make("div", "architecture-direction-legend");
    append(
      legend,
      make("span", "outgoing", "蓝色：它依赖谁 →"),
      make("span", "incoming", "琥珀：← 谁依赖它"),
    );
    panel.appendChild(legend);
    const list = make("div", "architecture-direct-list");
    relations.forEach((edge) => {
      const direction = edge.source_group_id === group.group_id ? "outgoing" : "incoming";
      const otherGroupId = direction === "outgoing" ? edge.target_group_id : edge.source_group_id;
      const button = make("button", `architecture-direct-relation ${direction}`);
      button.type = "button";
      button.dataset.groupEdgeId = edge.group_edge_id;
      button.setAttribute("aria-pressed", String(state.architectureSelectedRelation === edge.group_edge_id));
      append(
        button,
        make("span", "relation-direction", direction === "outgoing" ? "依赖 →" : "← 被依赖"),
        make("strong", "", architectureGroupLabel(otherGroupId)),
        make("span", "relation-count", `${edge.edge_count} 条`),
      );
      button.addEventListener("click", () => {
        state.architectureSelectedRelation = state.architectureSelectedRelation === edge.group_edge_id
          ? null
          : edge.group_edge_id;
        renderArchitecture();
        showToast(state.architectureSelectedRelation ? `已单独显示与${architectureGroupLabel(otherGroupId)}的关系` : "已恢复当前分区全部关系");
      });
      list.appendChild(button);
    });
    panel.appendChild(list);
    host.appendChild(panel);
  }

  function renderArchitectureInspector() {
    const host = byId("architecture-inspector");
    clear(host);
    const group = architectureGroups.get(state.architectureSelectedGroup);
    const node = state.architectureSelectedNode
      ? architectureNodes.get(state.architectureSelectedNode)
      : null;
    if (node) {
      const path = node.owned_paths?.[0] || "路径未知";
      const incoming = [...architectureEdges.values()].filter((edge) => edge.target_node_id === node.node_id);
      const outgoing = [...architectureEdges.values()].filter((edge) => edge.source_node_id === node.node_id);
      append(
        host,
        make("p", "eyebrow", "当前模块"),
        make("h3", "", architectureNodeLabel(node)),
        make("p", "tech-name", node.label),
        make("p", "", path),
      );
      const facts = make("div", "facts-grid");
      append(
        facts,
        fact("所在分区", architectureGroupLabel(node.group_id)),
        fact("对外依赖", `${outgoing.length} 条`),
        fact("被其他模块依赖", `${incoming.length} 条`),
        fact("公开接口", `${node.interfaces?.length || 0} 个`),
      );
      host.appendChild(facts);
      host.appendChild(make("p", "technical-note", "这些关系来自冻结代码中的静态 import，不证明运行时一定执行。"));
      const back = make("button", "secondary-button", "返回分区说明");
      back.type = "button";
      back.addEventListener("click", () => {
        state.architectureSelectedNode = null;
        renderArchitectureInspector();
        renderArchitectureModules();
      });
      host.appendChild(back);
      return;
    }
    if (!group) {
      append(
        host,
        make("p", "eyebrow", "系统全景"),
        make("h3", "", "先看全局，再按需深入"),
        make("p", "", "左侧是当前冻结版本的全部系统分区；高亮边框表示本次变化落在这里。点击任一分区，可查看职责、关系和模块。"),
      );
      const facts = make("div", "facts-grid");
      append(
        facts,
        fact("系统分区", `${architecture.coverage.group_count} 个`),
        fact("完整模块", `${architecture.coverage.node_count} 个`),
        fact("静态关系", `${architecture.coverage.edge_count} 条`),
        fact("本次涉及分区", `${architecture.change_overlay.group_ids.length} 个`),
      );
      host.appendChild(facts);
      return;
    }
    append(
      host,
      make("p", "eyebrow", group.lane === "support" ? "工程支撑分区" : "产品与运行分区"),
      make("h3", "", group.label),
      make("p", "", group.responsibility),
    );
    const facts = make("div", "facts-grid");
    append(
      facts,
      fact("模块", `${group.module_count} 个`),
      fact("内部关系", `${group.internal_edge_count} 条`),
      fact("流入分区", `${group.incoming_relation_count} 个`),
      fact("流出分区", `${group.outgoing_relation_count} 个`),
      fact("本次变化", `${group.changed_count} 个`),
      fact("分区来源", group.group_source === "confirmed_prd_v1.3_system_glossary" ? "已确认词表" : "待人工归类"),
    );
    host.appendChild(facts);
    renderArchitectureDirectRelations(host, group);
    const actions = make("div", "architecture-actions");
    const modules = make("button", "primary-button", state.architectureDepth === "modules" ? "收起内部结构" : "查看这个分区的内部结构");
    modules.type = "button";
    modules.setAttribute("aria-expanded", String(state.architectureDepth === "modules"));
    modules.addEventListener("click", () => {
      state.architectureDepth = state.architectureDepth === "modules" ? "overview" : "modules";
      state.architectureSelectedNode = null;
      state.architectureSelectedArea = null;
      state.architectureModuleDetailsOpen = false;
      state.architectureModuleLimit = 18;
      renderArchitectureInspector();
      renderArchitectureModules();
      if (state.architectureDepth === "modules") byId("architecture-modules").scrollIntoView({block: "nearest"});
    });
    actions.appendChild(modules);
    const overview = make("button", "secondary-button", "返回全部分区关系");
    overview.type = "button";
    overview.addEventListener("click", () => {
      state.architectureSelectedGroup = null;
      state.architectureSelectedRelation = null;
      state.architectureSelectedNode = null;
      state.architectureSelectedArea = null;
      state.architectureModuleDetailsOpen = false;
      state.architectureDepth = "overview";
      renderArchitecture();
    });
    actions.appendChild(overview);
    host.appendChild(actions);
  }

  function renderArchitectureRelations() {
    const host = byId("architecture-relations");
    clear(host);
    host.appendChild(make("h3", "technical-section-title", state.architectureSelectedGroup ? "当前分区的全部静态关系" : "全部分区关系"));
    const list = make("div", "architecture-relation-list");
    const relations = state.architectureSelectedGroup
      ? architecture.group_edges.filter((edge) => edge.source_group_id === state.architectureSelectedGroup || edge.target_group_id === state.architectureSelectedGroup)
      : architecture.group_edges;
    relations
      .slice()
      .sort((left, right) => right.edge_count - left.edge_count)
      .forEach((edge) => {
        const item = state.architectureSelectedGroup
          ? make("button", `architecture-relation ${architectureEdgeDirection(edge)}`)
          : make("div", "architecture-relation");
        if (item.tagName === "BUTTON") {
          item.type = "button";
          item.dataset.groupEdgeId = edge.group_edge_id;
          item.setAttribute("aria-pressed", String(state.architectureSelectedRelation === edge.group_edge_id));
          item.addEventListener("click", () => {
            state.architectureSelectedRelation = state.architectureSelectedRelation === edge.group_edge_id
              ? null
              : edge.group_edge_id;
            renderArchitecture();
          });
        }
        append(
          item,
          make("strong", "", `${architectureGroupLabel(edge.source_group_id)} → ${architectureGroupLabel(edge.target_group_id)}`),
          make("span", "", `${edge.edge_count} 条可追溯静态依赖`),
        );
        list.appendChild(item);
      });
    if (!relations.length) list.appendChild(make("p", "technical-note", "没有找到跨分区静态关系。"));
    host.appendChild(list);
  }

  function renderArchitectureModules() {
    const host = byId("architecture-modules");
    const group = architectureGroups.get(state.architectureSelectedGroup);
    host.hidden = state.architectureDepth !== "modules" || !group;
    clear(host);
    if (host.hidden) return;
    const nodes = group.node_ids.map((nodeId) => architectureNodes.get(nodeId)).filter(Boolean);
    const areas = architectureModuleAreas(group, nodes);
    const selectedArea = areas.find((area) => area.id === state.architectureSelectedArea) || null;
    const head = make("div", "architecture-modules-head");
    const copy = make("div", "");
    append(
      copy,
      make("h3", "", `${group.label} · 逐层查看`),
      make("p", "", `先从 ${areas.length} 个中文子区域理解结构；只有需要核对时，才展开具体源码模块。`),
    );
    const close = make("button", "secondary-button", "返回分区关系图");
    close.type = "button";
    close.addEventListener("click", () => {
      state.architectureDepth = "overview";
      state.architectureSelectedNode = null;
      state.architectureSelectedArea = null;
      state.architectureModuleDetailsOpen = false;
      renderArchitectureInspector();
      renderArchitectureModules();
      byId("architecture-canvas").focus({preventScroll: true});
    });
    append(head, copy, close);
    host.appendChild(head);

    const steps = make("ol", "module-layer-steps");
    [
      ["1", "系统分区", group.label, "done"],
      ["2", "中文子区域", selectedArea ? selectedArea.label : "请先选择", selectedArea ? "done" : "active"],
      ["3", "技术模块（可选）", state.architectureModuleDetailsOpen ? "已经展开" : "默认收起", state.architectureModuleDetailsOpen ? "active" : "optional"],
    ].forEach(([number, title, detail, status]) => {
      const step = make("li", `module-layer-step ${status}`);
      append(
        step,
        make("span", "module-step-number", number),
        append(make("span", "module-step-copy"), make("strong", "", title), make("small", "", detail)),
      );
      steps.appendChild(step);
    });
    host.appendChild(steps);
    host.appendChild(make("p", "module-layer-note", "这些子区域按源码位置自动整理，帮助阅读，不代表运行时先后顺序。"));

    const areaHeading = make("div", "module-area-heading");
    append(
      areaHeading,
      make("h4", "", "先选一个中文子区域"),
      make("p", "", "这里不显示代码名；你可以先理解系统由哪些部分组成。"),
    );
    host.appendChild(areaHeading);
    const areaGrid = make("div", "module-area-grid");
    areas.forEach((area, index) => {
      const button = make("button", "module-area-card");
      button.type = "button";
      button.dataset.moduleAreaId = area.id;
      button.dataset.areaCount = String(area.nodes.length);
      button.setAttribute("aria-pressed", String(selectedArea?.id === area.id));
      const body = make("span", "module-area-body");
      append(
        body,
        make("strong", "", area.label),
        make("span", "module-area-description", area.description),
      );
      const meta = make("span", "module-area-meta");
      append(
        meta,
        make("span", "", `${area.nodes.length} 个模块`),
        area.involvedCount ? make("span", "involved", `本次涉及 ${area.involvedCount}`) : null,
      );
      append(button, make("span", "module-area-number", String(index + 1).padStart(2, "0")), body, meta);
      button.addEventListener("click", () => {
        state.architectureSelectedArea = area.id;
        state.architectureSelectedNode = null;
        state.architectureModuleDetailsOpen = false;
        state.architectureModuleLimit = 18;
        renderArchitectureInspector();
        renderArchitectureModules();
        showToast(`已选择${area.label}`);
      });
      areaGrid.appendChild(button);
    });
    host.appendChild(areaGrid);

    if (!selectedArea) return;
    const summary = make("section", "module-area-summary");
    const summaryHead = make("div", "module-area-summary-head");
    append(
      summaryHead,
      append(make("div", ""), make("p", "eyebrow", "第 2 层 · 当前子区域"), make("h4", "", selectedArea.label), make("p", "", selectedArea.description)),
    );
    const changeArea = make("button", "secondary-button", "换一个子区域");
    changeArea.type = "button";
    changeArea.addEventListener("click", () => {
      state.architectureSelectedArea = null;
      state.architectureSelectedNode = null;
      state.architectureModuleDetailsOpen = false;
      state.architectureModuleLimit = 18;
      renderArchitectureInspector();
      renderArchitectureModules();
    });
    summaryHead.appendChild(changeArea);
    summary.appendChild(summaryHead);
    const summaryFacts = make("div", "module-area-facts");
    append(
      summaryFacts,
      fact("包含模块", `${selectedArea.nodes.length} 个`),
      fact("对外入口", `${selectedArea.interfaceCount} 个`),
      fact("本次涉及", `${selectedArea.involvedCount} 个`),
      fact("分组依据", "源码目录"),
    );
    summary.appendChild(summaryFacts);
    const reveal = make("button", "primary-button module-detail-toggle", state.architectureModuleDetailsOpen ? "收起技术模块" : "展开技术模块（可选）");
    reveal.type = "button";
    reveal.setAttribute("aria-expanded", String(state.architectureModuleDetailsOpen));
    reveal.addEventListener("click", () => {
      state.architectureModuleDetailsOpen = !state.architectureModuleDetailsOpen;
      state.architectureSelectedNode = null;
      state.architectureModuleLimit = 18;
      renderArchitectureInspector();
      renderArchitectureModules();
    });
    summary.appendChild(reveal);
    host.appendChild(summary);

    if (!state.architectureModuleDetailsOpen) return;
    const technicalHead = make("div", "module-technical-head");
    append(
      technicalHead,
      make("h4", "", `${selectedArea.label} · 技术模块`),
      make("p", "", `以下是核对源码时才需要看的技术层。当前显示 ${Math.min(selectedArea.nodes.length, state.architectureModuleLimit)} / ${selectedArea.nodes.length}。`),
    );
    host.appendChild(technicalHead);
    const changed = changedNodeSet();
    const grid = make("div", "module-grid");
    selectedArea.nodes.slice(0, state.architectureModuleLimit).forEach((node) => {
      const button = make("button", `module-card${changed.has(node.node_id) ? " changed" : ""}`);
      button.type = "button";
      button.dataset.architectureNodeId = node.node_id;
      button.setAttribute("aria-selected", String(state.architectureSelectedNode === node.node_id));
      append(
        button,
        make("strong", "", architectureNodeLabel(node)),
        make("span", "", node.owned_paths?.[0] || node.label),
      );
      button.addEventListener("click", () => {
        state.architectureSelectedNode = node.node_id;
        renderArchitectureInspector();
        renderArchitectureModules();
      });
      grid.appendChild(button);
    });
    host.appendChild(grid);
    if (selectedArea.nodes.length > state.architectureModuleLimit) {
      const more = make("button", "branch-button module-more", `再显示 ${Math.min(18, selectedArea.nodes.length - state.architectureModuleLimit)} 个模块`);
      more.type = "button";
      more.addEventListener("click", () => {
        state.architectureModuleLimit += 18;
        renderArchitectureModules();
      });
      host.appendChild(more);
    }
  }

  function renderArchitecture() {
    if (!architecture) return;
    renderArchitectureHeader();
    renderArchitectureGroups();
    renderArchitectureInspector();
    renderArchitectureRelations();
    renderArchitectureModules();
    window.requestAnimationFrame(drawArchitectureLinks);
  }

  function selectedLinks(view) {
    const linked = new Set();
    if (!state.selectedId) return linked;
    linked.add(state.selectedId);
    view.paths.forEach((path) => {
      if (path.changed_node_id === state.selectedId || path.impacted_node_id === state.selectedId) {
        linked.add(path.changed_node_id);
        linked.add(path.impacted_node_id);
      }
    });
    return linked;
  }

  function nodeButton(node, linked) {
    const button = make("button", `flow-node ${node.status}`);
    button.type = "button";
    button.dataset.nodeId = node.node_id;
    button.setAttribute("aria-selected", String(state.selectedId === node.node_id));
    if (state.focusPath && state.selectedId && !linked.has(node.node_id)) button.classList.add("focus-dim");
    append(
      button,
      make("span", "node-icon", nodeIcon(node.status)),
      make("span", "node-label", node.label),
      make("span", "node-state", node.status_label),
      make("span", "node-tech", node.technical_label),
    );
    button.addEventListener("click", () => {
      state.selectedId = node.node_id;
      renderGraph();
      renderInspector();
      if (state.evidenceOpen) renderTechnical();
    });
    return button;
  }

  function renderGraph() {
    const view = data.views[state.view];
    const host = byId("graph");
    clear(host);
    const nodeIndex = new Map(view.nodes.map((node) => [node.node_id, node]));
    const linked = selectedLinks(view);
    const relevantPaths = state.focusPath && state.selectedId
      ? view.paths.filter((path) => path.changed_node_id === state.selectedId || path.impacted_node_id === state.selectedId)
      : view.paths;
    const shownPaths = relevantPaths.slice(0, 6);
    const used = new Set();

    shownPaths.forEach((path) => {
      const changed = nodeIndex.get(path.changed_node_id);
      const impacted = nodeIndex.get(path.impacted_node_id);
      if (!changed || !impacted) return;
      used.add(changed.node_id);
      used.add(impacted.node_id);
      const row = make("div", "path-row");
      append(
        row,
        nodeButton(changed, linked),
        make("div", "path-arrow", `→ ${path.relation_label} →`),
        nodeButton(impacted, linked),
      );
      host.appendChild(row);
    });

    const standalone = view.nodes.filter((node) => !used.has(node.node_id));
    if (standalone.length) {
      const group = make("div", "standalone-nodes");
      standalone.forEach((node) => group.appendChild(nodeButton(node, linked)));
      host.appendChild(group);
    }
    if (!view.nodes.length) {
      host.appendChild(make("p", "technical-note", "这个视图没有可显示的已验证节点。"));
    }
    if (relevantPaths.length > shownPaths.length) {
      host.appendChild(
        make("p", "branch-note", `另有 ${relevantPaths.length - shownPaths.length} 条已确认代码关联，完整关系保留在技术依据和 JSON 中。`),
      );
    }

    document.querySelectorAll("[data-view]").forEach((button) => {
      button.setAttribute("aria-selected", String(button.dataset.view === state.view));
    });
    const descriptions = {
      before: "查看修改前存在的职责和确定性代码关联；新增职责在此视图中不会出现。",
      after: "查看修改后的职责和确定性代码关联；点击任一节点查看证据边界。",
      diff: "只显示新增、移除、改变或有关联的节点；未变化上下文被收起。",
    };
    byId("view-description").textContent = descriptions[state.view];
  }

  function renderBranches() {
    const host = byId("branch-zone");
    clear(host);
    const total = data.branch_groups.reduce((sum, group) => sum + group.count, 0);
    if (!total) {
      host.appendChild(make("p", "branch-note", "没有被折叠的代码关联位置。"));
      return;
    }
    if (state.branchLevel === 0) {
      const open = make("button", "branch-button", `还有 ${total} 个静态关联位置`);
      open.type = "button";
      open.setAttribute("aria-expanded", "false");
      open.addEventListener("click", () => {
        state.branchLevel = 1;
        state.branchGroup = null;
        renderBranches();
      });
      host.appendChild(open);
      return;
    }
    if (state.branchLevel === 1) {
      const groups = make("div", "branch-groups");
      data.branch_groups.forEach((group) => {
        const button = make("button", "branch-button", `${group.label} · ${group.count}`);
        button.type = "button";
        button.addEventListener("click", () => {
          state.branchLevel = 2;
          state.branchGroup = group.id;
          renderBranches();
        });
        groups.appendChild(button);
      });
      const collapse = make("button", "branch-button", "收起这一层");
      collapse.type = "button";
      collapse.addEventListener("click", () => {
        state.branchLevel = 0;
        state.branchGroup = null;
        renderBranches();
      });
      groups.appendChild(collapse);
      append(host, groups, make("p", "branch-note", "这里先按证据类型分组；再次点击才显示具体技术 ID。"));
      return;
    }
    const group = data.branch_groups.find((item) => item.id === state.branchGroup);
    if (!group) {
      state.branchLevel = 1;
      renderBranches();
      return;
    }
    host.appendChild(make("h3", "technical-section-title", `${group.label} · ${group.count}`));
    const ids = make("div", "id-grid");
    group.node_ids.forEach((id) => ids.appendChild(make("span", "id-pill", id)));
    host.appendChild(ids);
    host.appendChild(make("p", "branch-note", group.limitation));
    const tools = make("div", "branch-tools");
    const back = make("button", "branch-button", "返回分组");
    back.type = "button";
    back.addEventListener("click", () => {
      state.branchLevel = 1;
      state.branchGroup = null;
      renderBranches();
    });
    const collapse = make("button", "branch-button", "全部收起");
    collapse.type = "button";
    collapse.addEventListener("click", () => {
      state.branchLevel = 0;
      state.branchGroup = null;
      renderBranches();
    });
    append(tools, back, collapse);
    host.appendChild(tools);
  }

  function detailRow(icon, title, text) {
    const row = make("div", "detail-row");
    const copy = make("div", "");
    append(copy, make("h3", "", title), make("p", "", text));
    return append(row, make("div", "detail-icon", icon), copy);
  }

  function renderInspector() {
    const title = byId("inspector-title");
    const tech = byId("inspector-tech");
    const body = byId("inspector-body");
    clear(body);
    const detail = state.selectedId ? data.node_details[state.selectedId] : null;
    if (!detail) {
      title.textContent = "请选择一个职责节点";
      tech.textContent = "";
      body.appendChild(make("p", "technical-note", "点击变化图中的节点，即可查看它原来负责什么、这次怎样变以及证据边界。"));
      return;
    }
    title.textContent = detail.label;
    tech.textContent = `${detail.technical_label} · ${detail.status_label}`;
    append(
      body,
      detailRow("前", "它原来负责什么", detail.before),
      detailRow("后", "这次怎样变了", detail.after),
      detailRow("及", "谁可能直接受到影响", detail.impact),
      detailRow("证", "证据能证明到哪里", detail.evidence_boundary),
      detailRow("?", "哪里仍不清楚", detail.unknown),
    );
    const actions = make("div", "inspector-actions");
    const focus = make("button", "primary-button", state.focusPath ? "恢复完整关系" : "只看这条关联");
    focus.type = "button";
    focus.addEventListener("click", () => {
      state.focusPath = !state.focusPath;
      renderGraph();
      renderInspector();
    });
    const evidence = make("button", "secondary-button", "查看依据");
    evidence.type = "button";
    evidence.addEventListener("click", () => openTechnical(evidence));
    append(actions, focus, evidence);
    body.appendChild(actions);
  }

  function fact(label, value) {
    const item = make("div", "fact");
    append(item, make("small", "", label), make("strong", "", value));
    return item;
  }

  function renderTechnical() {
    const host = byId("technical-content");
    clear(host);
    host.appendChild(make("p", "technical-note", "以下内容是上面结论的依据，不是另一份 AI 总结。页面只读取冻结样本的派生数据。"));
    const facts = make("div", "facts-grid");
    append(
      facts,
      fact("变化文件", `${data.change.changed_files} 个`),
      fact("Base", String(data.change_identity.base_ref).slice(0, 12)),
      fact("Head", String(data.change_identity.head_ref).slice(0, 12)),
      fact("Patch", String(data.change_identity.patch_sha256).slice(0, 12)),
      fact("结构基线", data.baseline_validation.status),
      fact("Claim", `${data.validation.claim_count} 条`),
      fact("图中节点", `${data.validation.displayed_node_count} 个`),
      fact("结构边", `${data.validation.edge_count} 条`),
      fact("明确折叠", `${data.validation.omitted_node_count} 个`),
      architecture ? fact("系统分区", `${architecture.coverage.group_count} 个`) : null,
      architecture ? fact("完整系统模块", `${architecture.coverage.node_count} 个`) : null,
      architecture ? fact("完整静态关系", `${architecture.coverage.edge_count} 条`) : null,
    );
    host.appendChild(facts);

    const selected = state.selectedId ? data.node_details[state.selectedId] : null;
    if (selected) {
      host.appendChild(make("h3", "technical-section-title", "当前节点"));
      const list = make("ul", "technical-list");
      [
        `Node ID：${selected.node_id}`,
        `中文标签来源：${selected.label_source}`,
        `路径：${selected.owned_paths.join("、") || "无"}`,
        `接口：${selected.interfaces.join("、") || "无"}`,
        `证据引用：${selected.evidence_refs.join("、") || "无"}`,
      ].forEach((text) => list.appendChild(make("li", "", text)));
      host.appendChild(list);
    }

    host.appendChild(make("h3", "technical-section-title", "全部已校验结论"));
    const selectedClaims = new Set(selected ? selected.claim_ids : []);
    data.claims.forEach((claim) => {
      const details = make("details", "claim");
      if (selectedClaims.has(claim.id)) details.open = true;
      const summary = make("summary", "");
      const truth = claim.claim_type === "verified_fact" ? "verified" : claim.claim_type === "inference" ? "inference" : "unknown";
      const truthLabel = truth === "verified" ? "已证实" : truth === "inference" ? "有依据的推断" : "尚不清楚";
      append(summary, make("span", `truth ${truth}`, truthLabel), make("span", "claim-copy", `${claim.section} · ${claim.text}`));
      const body = make("div", "claim-body");
      [
        `Claim ID：${claim.id}`,
        `证据：${claim.evidence_ids.join("、") || "无"}`,
        `限制：${claim.limitations.join("；") || "无"}`,
        claim.next_check ? `最小检查：${claim.next_check}` : null,
      ].filter(Boolean).forEach((text) => body.appendChild(make("div", "", text)));
      append(details, summary, body);
      host.appendChild(details);
    });

    if (data.limitations.length) {
      host.appendChild(make("h3", "technical-section-title", "架构分析限制"));
      const list = make("ul", "technical-list");
      data.limitations.forEach((item) => list.appendChild(make("li", "", item)));
      host.appendChild(list);
    }
  }

  function openTechnical(trigger) {
    state.evidenceOpen = true;
    const toggle = byId("technical-toggle");
    const content = byId("technical-content");
    toggle.setAttribute("aria-expanded", "true");
    content.hidden = false;
    renderTechnical();
    content.scrollIntoView({block: "nearest"});
    if (trigger) trigger.dataset.openedEvidence = "true";
  }

  function closeTechnical() {
    state.evidenceOpen = false;
    byId("technical-toggle").setAttribute("aria-expanded", "false");
    byId("technical-content").hidden = true;
  }

  function bindEvents() {
    document.querySelectorAll("[data-page]").forEach((button) => {
      button.addEventListener("click", () => switchPage(button.dataset.page));
    });
    document.querySelectorAll("[data-view]").forEach((button) => {
      button.addEventListener("click", () => {
        state.view = button.dataset.view;
        renderGraph();
        renderInspector();
        if (state.evidenceOpen) renderTechnical();
        showToast(`已切换到${button.textContent}`);
      });
    });
    byId("close-inspector").addEventListener("click", () => {
      state.selectedId = null;
      state.focusPath = false;
      renderGraph();
      renderInspector();
    });
    byId("technical-toggle").addEventListener("click", () => {
      if (state.evidenceOpen) closeTechnical(); else openTechnical(byId("technical-toggle"));
    });
    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      if (state.summaryContextOpen) {
        state.summaryContextOpen = false;
        renderSummary();
        document.querySelector('[data-summary-context="summary.why"]')?.focus();
        return;
      }
      if (state.page === "architecture") {
        if (state.architectureSelectedRelation) {
          state.architectureSelectedRelation = null;
          renderArchitecture();
        } else if (state.architectureSelectedNode) {
          state.architectureSelectedNode = null;
          renderArchitectureInspector();
          renderArchitectureModules();
        } else if (state.architectureModuleDetailsOpen) {
          state.architectureModuleDetailsOpen = false;
          state.architectureModuleLimit = 18;
          renderArchitectureModules();
        } else if (state.architectureSelectedArea) {
          state.architectureSelectedArea = null;
          renderArchitectureModules();
        } else if (state.architectureDepth === "modules") {
          state.architectureDepth = "overview";
          renderArchitectureInspector();
          renderArchitectureModules();
        } else if (state.architectureSelectedGroup) {
          state.architectureSelectedGroup = null;
          renderArchitecture();
        }
        return;
      }
      if (state.evidenceOpen) {
        closeTechnical();
        byId("technical-toggle").focus();
      } else if (state.selectedId) {
        state.selectedId = null;
        state.focusPath = false;
        renderGraph();
        renderInspector();
        byId("graph").focus({preventScroll: true});
      }
    });
    let resizeTimer;
    window.addEventListener("resize", () => {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(drawArchitectureLinks, 100);
    });
  }

  renderHeader();
  renderSummary();
  renderGraph();
  renderBranches();
  renderInspector();
  bindEvents();
  if (!architecture) {
    const architectureTab = document.querySelector('[data-page="architecture"]');
    architectureTab.disabled = true;
    architectureTab.title = "当前样本没有整体架构快照";
  }
  switchPage("change", false);
})();
