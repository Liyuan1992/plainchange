(() => {
  "use strict";

  const sourceData = JSON.parse(document.getElementById("review-data").textContent);
  const reviewTranslation = JSON.parse(document.getElementById("localized-review-data").textContent)[window.PlainChangeI18n.locale];
  function projectReview(value) {
    if (reviewTranslation?.schema_version === "plainchange.generated-review-presentation.v1") {
      const root = value?.schema_version === "change-passport.system-architecture.v1"
        ? "architecture"
        : "review";
      for (const message of reviewTranslation.messages || []) {
        if (message.root !== root || !Array.isArray(message.path) || !message.path.length) continue;
        let parent = value;
        for (const part of message.path.slice(0, -1)) {
          if (parent === null || typeof parent !== "object" || !(part in parent)) {
            parent = null;
            break;
          }
          parent = parent[part];
        }
        const leaf = message.path.at(-1);
        if (parent !== null && typeof parent === "object" && typeof parent[leaf] === "string") {
          parent[leaf] = message.text;
        }
      }
      return value;
    }
    if (!reviewTranslation?.translations) return value;
    const {translations, fields, arrays, skip} = reviewTranslation;
    const translated = text => Object.prototype.hasOwnProperty.call(translations, text) ? translations[text] : text;
    const walk = (item) => {
      if (Array.isArray(item)) return item.map(walk);
      if (!item || typeof item !== 'object') return item;
      return Object.fromEntries(Object.entries(item).map(([key, child]) => {
        if (skip.includes(key)) return [key, child];
        if (fields.includes(key) && typeof child === 'string') return [key, translated(child)];
        if (arrays.includes(key) && Array.isArray(child)) return [key, child.map(text => typeof text === 'string' ? translated(text) : walk(text))];
        return [key, walk(child)];
      }));
    };
    return walk(value);
  }
  const data = projectReview(sourceData);
  const sourceControl = JSON.parse(document.getElementById("software-control-data").textContent);
  const controlTranslations = JSON.parse(document.getElementById("localized-control-data").textContent);
  const softwareControl = controlTranslations[window.PlainChangeI18n.locale] || sourceControl;
  const languageBoundary = document.querySelector('.language-boundary');
  if (languageBoundary && sourceControl) {
    languageBoundary.textContent = window.PlainChangeI18n.locale === 'zh-CN'
      ? '报告说明支持独立译文；引用原话与技术证据保留原文，语言切换不改变证据状态。'
      : controlTranslations[window.PlainChangeI18n.locale]
      ? 'PlainChange-generated explanations are shown in English. Project descriptions, original quotations and technical evidence remain in their source language. Evidence states are unchanged.'
      : window.PlainChangeI18n.locale === 'en'
        ? 'English report text is not available for this report. The interface is translated; report text remains in its source language.'
        : '报告说明支持独立译文；引用原话与技术证据保留原文，语言切换不改变证据状态。';
  }
  const technicalPayload = JSON.parse(document.getElementById("technical-payload-data").textContent);
  const agentProvenance = JSON.parse(document.getElementById("agent-provenance-data").textContent);
  let architecture = data.system_architecture || null;
  const conceptualArchitecture = data.conceptual_architecture;
  let architectureGroups = new Map();
  let architectureGroupEdges = new Map();
  let architectureNodes = new Map();
  let architectureEdges = new Map();
  let architectureModuleAreaRules = [];
  let architectureLoadPromise = null;

  function indexArchitecture() {
    architectureGroups = new Map((architecture?.groups || []).map((group) => [group.group_id, group]));
    architectureGroupEdges = new Map((architecture?.group_edges || []).map((edge) => [edge.group_edge_id, edge]));
    architectureNodes = new Map((architecture?.nodes || []).map((node) => [node.node_id, node]));
    architectureEdges = new Map((architecture?.edges || []).map((edge) => [edge.edge_id, edge]));
    architectureModuleAreaRules = Array.isArray(architecture?.target_profile?.module_areas)
      ? architecture.target_profile.module_areas
      : [];
  }

  async function sha256Hex(bytes) {
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
  }

  async function decodeTechnicalPayload() {
    if (!technicalPayload || technicalPayload.encoding !== "gzip+base64") return null;
    if (typeof DecompressionStream !== "function") throw new Error("当前浏览器不支持离线解压技术快照");
    const binary = atob(technicalPayload.data);
    const compressed = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    if (await sha256Hex(compressed) !== technicalPayload.compressed_sha256) throw new Error("技术快照压缩内容校验失败");
    const stream = new Blob([compressed]).stream().pipeThrough(new DecompressionStream("gzip"));
    const raw = new Uint8Array(await new Response(stream).arrayBuffer());
    if (await sha256Hex(raw) !== technicalPayload.sha256) throw new Error("技术快照内容校验失败");
    return JSON.parse(new TextDecoder().decode(raw));
  }

  async function ensureArchitectureLoaded() {
    if (architecture) return true;
    if (!technicalPayload) return false;
    if (!architectureLoadPromise) {
      const status = byId("technical-payload-status");
      if (status) {
        status.textContent = "正在打开完整技术证据…";
        status.hidden = false;
      }
      architectureLoadPromise = decodeTechnicalPayload()
        .then((value) => {
          architecture = projectReview(value);
          indexArchitecture();
          if (status) status.hidden = true;
          return true;
        })
        .catch((error) => {
          architectureLoadPromise = null;
          const message = error instanceof Error ? error.message : "技术快照加载失败";
          if (status) {
            status.textContent = `技术实现暂时无法打开：${message}。负责人说明仍可阅读，但请不要把技术证据当成已经加载。`;
            status.hidden = false;
          }
          if (!softwareControl && byId("architecture-scope")) {
            byId("architecture-scope").textContent = `技术实现暂时无法打开：${message}。请不要把空白页面理解为已经没有技术证据。`;
          }
          showToast(message);
          return false;
        });
    }
    return architectureLoadPromise;
  }

  indexArchitecture();
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
    architectureSelectedConcept: null,
    architectureSelectedRelation: null,
    architectureSelectedNode: null,
    architectureSelectedArea: null,
    architectureModuleDetailsOpen: false,
    architectureDepth: "overview",
    architectureModuleLimit: 18,
    conceptLayout: null,
    ownerMapSelectedId: softwareControl?.working_map?.nodes?.find((node) => node.change_state === "changed")?.id
      || softwareControl?.working_map?.nodes?.[0]?.id
      || null,
    ownerOverviewSelectedId: softwareControl?.working_map?.overview_map?.nodes?.find((node) => node.change_state === "changed")?.id
      || softwareControl?.working_map?.overview_map?.nodes?.[0]?.id
      || null,
    ownerExpandedOverviewId: null,
    ownerMapLayout: null,
  };

  const byId = (id) => document.getElementById(id);
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };
  const sourceText = (tag, className, text) => {
    const node = make(tag, className, text);
    node.dataset.preserveLanguage = "true";
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
    byId("brand-mark").textContent = data.header.brand.mark;
    byId("brand-name").textContent = data.header.brand.name;
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
    if (softwareControl) {
      byId("eyebrow").textContent = "软件变化掌控报告";
      byId("page-title").textContent = softwareControl.product.name;
      byId("subtitle").textContent = softwareControl.product.purpose;
      byId("scope-note").textContent = softwareControl.first_screen_summary.residual_risk.text;
      byId("change-tab").textContent = "这次改了什么";
      byId("architecture-tab").textContent = "这个软件怎么工作";
      clear(host);
      [
        ["good", softwareControl.first_screen_summary.confirmed_change.state_label],
        ["info", softwareControl.first_screen_summary.user_impact.state_label],
        ["warn", softwareControl.first_screen_summary.residual_risk.state_label],
      ].forEach(([tone, label]) => host.appendChild(make("span", `chip ${tone}`, label)));
    }
  }

  function renderOwnerStatus() {
    const summary = softwareControl.first_screen_summary;
    const modeBanner = byId("analysis-mode-banner");
    if (softwareControl.analysis_mode === "basic_evidence") {
      modeBanner.hidden = false;
      clear(modeBanner);
      append(
        modeBanner,
        make("strong", "", "基础证据模式：还没有让模型理解这个软件"),
        make("span", "", "下面只展示固定代码事实、结构线索和未知项。它不能替代完整的业务理解，也不应被当成最终结论。"),
      );
    } else {
      modeBanner.hidden = true;
    }
    byId("owner-change-headline").textContent = summary.headline;
    byId("owner-confirmed-copy").textContent = summary.confirmed_change.text;
    const meta = byId("owner-change-meta");
    clear(meta);
    append(meta, stateDisclosure(summary.confirmed_change), make("span", "owner-concept-label", `涉及内部：${summary.internal_concept_label}`));
    const changeLocation = ownerChangeLocation();
    if (changeLocation) {
      const capabilityMap = softwareControl?.working_map?.map_kind === "capability_map";
      const locationLink = make("button", "owner-location-link", capabilityMap ? "在软件能力图中查看 →" : "在软件流程中查看 →");
      locationLink.type = "button";
      locationLink.dataset.ownerLocationLink = changeLocation.detail.id;
      locationLink.setAttribute("aria-label", `${capabilityMap ? "在软件能力图中查看" : "在软件流程中查看"}：${changeLocation.detail.label}`);
      locationLink.addEventListener("click", openOwnerChangeLocation);
      meta.appendChild(locationLink);
    }
    const host = byId("owner-status-list");
    clear(host);
    const verification = data.verification_control;
    if (!verification) {
      [
        ["impact", "影", "会影响我现在的软件吗？", summary.user_impact],
        ["risk", "!", "我需要担心什么？", summary.residual_risk],
        ["action", "✓", "我现在该怎么办？", summary.owner_action],
      ].forEach(([tone, icon, question, item]) => {
        const row = make("article", `owner-status-row ${tone}`);
        const copy = make("div", "owner-status-copy");
        append(copy, append(make("div", "owner-status-heading"), make("strong", "", question), stateDisclosure(item)), make("p", "", item.text));
        append(row, make("span", "owner-status-icon", icon), copy);
        host.appendChild(row);
      });
      return;
    }

    const english = window.PlainChangeI18n.locale === "en";
    const localized = (value) => value && typeof value === "object"
      ? (value[window.PlainChangeI18n.locale] || value.en || value["zh-CN"] || "")
      : String(value || "");
    const verificationGrid = make("div", "owner-verification-grid");
    const donePanel = make("section", "owner-control-panel owner-verified-panel");
    const doneHeading = append(make("div", "owner-control-heading"), make("span", "owner-control-icon verified", "✓"), append(make("div", ""), make("p", "eyebrow", english ? "Completed checks" : "已完成检查"), make("h3", "", english ? "Already verified for you" : "已经替你验证")));
    donePanel.appendChild(doneHeading);
    const passed = verification.passed_checks || [];
    if (!passed.length) {
      donePanel.appendChild(make("p", "owner-empty-verification", english ? "No structured verification receipt was provided. This does not mean a check failed." : "这份报告没有收到结构化验证收据；这不代表检查失败。"));
    } else {
      const list = make("div", "owner-verification-list");
      passed.forEach((check) => {
        const item = make("article", "owner-verification-item passed");
        append(item, make("span", "owner-verification-mark", "✓"), append(make("div", ""), make("strong", "", localized(check.label)), make("p", "", localized(check.summary)), make("small", "", `${english ? "Verified scope" : "验证范围"}：${localized(check.scope)}`)));
        list.appendChild(item);
      });
      donePanel.appendChild(list);
    }
    verificationGrid.appendChild(donePanel);

    const gapsPanel = make("section", "owner-control-panel owner-gaps-panel");
    gapsPanel.appendChild(append(make("div", "owner-control-heading"), make("span", "owner-control-icon gap", "?"), append(make("div", ""), make("p", "eyebrow", english ? "Remaining boundary" : "剩余边界"), make("h3", "", english ? "What is not verified, and why?" : "还有什么没验证，为什么？"))));
    const gaps = verification.gaps || [];
    if (!gaps.length) {
      gapsPanel.appendChild(make("p", "owner-empty-verification", english ? "No remaining verification gap was identified from the supplied evidence." : "现有证据没有列出仍需处理的验证缺口。"));
    } else {
      const list = make("div", "owner-gap-list");
      gaps.forEach((gap) => {
        const item = make("article", "owner-gap-item");
        append(item, make("strong", "", localized(gap.label)), make("p", "", `${english ? "Why" : "为什么"}：${localized(gap.reason)}`), make("p", "", `${english ? "How to verify" : "怎么验证"}：${localized(gap.how)}`), make("small", "", `${english ? "Handled by" : "由谁处理"}：${localized(gap.responsibility)}`));
        list.appendChild(item);
      });
      gapsPanel.appendChild(list);
    }
    verificationGrid.appendChild(gapsPanel);
    host.appendChild(verificationGrid);

    const decision = verification.decision;
    const decisionPanel = make("article", `owner-decision-panel ${decision.tone}`);
    const decisionCopy = append(make("div", ""), make("p", "eyebrow", english ? "Your decision" : "需要你决定"), make("h3", "", localized(decision.title)), make("p", "", localized(decision.text)));
    const decisionItems = decision.items || [];
    if (decisionItems.length) {
      const list = make("ul", "owner-decision-list");
      decisionItems.forEach((item) => {
        const row = make("li", "owner-decision-item");
        append(row, make("strong", "", localized(item.label)), make("small", "", `${english ? "Handled by" : "由谁处理"}：${localized(item.responsibility)}`));
        list.appendChild(row);
      });
      decisionCopy.appendChild(list);
    }
    append(decisionPanel, make("span", "owner-decision-icon", decision.tone === "stop" ? "!" : "人"), decisionCopy);
    host.appendChild(decisionPanel);
    host.appendChild(make("p", "owner-verification-boundary", localized(verification.boundary)));
  }

  function stateDisclosure(item) {
    const details = make("details", "owner-state-details");
    details.appendChild(make("summary", "owner-state-label", item.state_label));
    details.appendChild(make("p", "", item.state_explanation));
    return details;
  }

  function renderAgentProvenance() {
    const host = byId("owner-provenance");
    if (!host || !agentProvenance) return;
    host.hidden = false;
    clear(host);
    const english = window.PlainChangeI18n.locale === "en";
    const statusCopy = {
      available: english ? ["Authorship recorded", "The selected change has recorded authorship for all added lines."] : ["已有记录", "这次新增代码都找到了来源记录。"],
      partial: english ? ["Partially recorded", "Some added lines still have no recorded authorship."] : ["部分记录", "部分新增代码仍然没有来源记录。"],
      no_record: english ? ["No historical record", "Git AI is installed, but these changes were made before an authorship record was captured. PlainChange will not guess the author afterwards."] : ["没有历史记录", "Git AI 已安装，但这批变化发生时没有留下来源记录；PlainChange 不会事后猜测作者。"],
      not_installed: english ? ["Not recorded", "This change has no AI authorship record. After Git AI is installed, future changes can be recorded; earlier changes cannot be reconstructed automatically."] : ["尚未记录", "这次变化没有记录 AI 来源。安装 Git AI 后，可以从未来的变化开始记录；以前没有记录的变化不能自动补回。"],
      invalid: english ? ["Record unavailable", "An authorship record was found but could not be safely matched to this change."] : ["记录不可用", "找到了来源数据，但它无法安全地与这次变化对应。"],
    }[agentProvenance.status] || (english ? ["Record unavailable", "No usable authorship summary is available."] : ["记录不可用", "目前没有可用的来源摘要。"]);
    const heading = make("div", "owner-provenance-heading");
    const title = make("div", "");
    append(title, make("p", "eyebrow", english ? "Code provenance" : "代码来源"), make("h2", "", english ? "Where did this change come from?" : "这次改动从哪里来"));
    append(heading, title, make("span", `owner-provenance-state ${agentProvenance.status}`, statusCopy[0]));
    host.appendChild(heading);
    host.appendChild(make("p", "owner-provenance-copy", statusCopy[1]));

    const summary = agentProvenance.summary;
    if (["available", "partial", "no_record"].includes(agentProvenance.status)) {
      const metrics = make("div", "owner-provenance-metrics");
      const tools = summary.tools.length
        ? summary.tools.map((item) => item.model === "unknown" ? item.tool : `${item.tool} · ${item.model}`).join(english ? ", " : "、")
        : (english ? "No tool identified" : "未识别工具");
      [
        [english ? "AI-recorded additions" : "AI 记录的新增代码", `${summary.ai_added_lines}`],
        [english ? "Human-recorded additions" : "人工记录的新增代码", `${summary.human_added_lines}`],
        [english ? "Additions without a source record" : "未留下来源记录的新增代码", `${summary.untracked_added_lines}`],
        [english ? "Recorded sessions" : "记录到的会话", `${summary.session_count}`],
      ].forEach(([label, value]) => {
        const metric = make("div", "owner-provenance-metric");
        append(metric, make("span", "", label), make("strong", "", value));
        metrics.appendChild(metric);
      });
      host.appendChild(metrics);
      const toolRow = make("p", "owner-provenance-tools");
      append(toolRow, make("strong", "", english ? "Recorded tool/model: " : "记录到的工具/模型："), make("span", "", tools));
      host.appendChild(toolRow);
    }
    host.appendChild(make("p", "owner-provenance-warning", english ? "Authorship records show where code came from. They do not prove that the software works correctly." : "来源记录只能说明代码从哪里来，不能证明软件功能正确。"));
  }

  function renderComparison(host, comparison) {
    if (!comparison) return;
    host.appendChild(make("h4", "owner-comparison-title", comparison.title));
    const grid = make("div", "owner-comparison");
    [["before", "以前", comparison.before], ["after", "现在", comparison.after]].forEach(([tone, title, steps]) => {
      const card = make("section", `owner-comparison-card ${tone}`);
      card.appendChild(make("strong", "", title));
      const list = make("ol", "owner-step-list");
      (steps || []).forEach((step) => list.appendChild(make("li", "", step)));
      card.appendChild(list);
      grid.appendChild(card);
    });
    host.appendChild(grid);
  }

  function renderOwnerQuestions() {
    const host = byId("owner-questions");
    clear(host);
    const primaryColumn = make("div", "owner-question-column owner-question-column-primary");
    const secondaryColumn = make("div", "owner-question-column owner-question-column-secondary");
    append(host, primaryColumn, secondaryColumn);
    softwareControl.five_questions.forEach((item, index) => {
      const section = make("article", `owner-question owner-question-${item.id}`);
      const head = make("div", "owner-question-head");
      append(
        head,
        make("span", "owner-question-number", String(index + 1).padStart(2, "0")),
        append(make("div", ""), make("h3", "", item.question), make("span", "owner-question-state", item.state_label)),
      );
      append(section, head, make("p", "owner-answer", item.answer));
      const details = item.details || {};
      if (Array.isArray(details.software_steps)) {
        const list = make("ol", "owner-software-steps");
        details.software_steps.forEach((step) => list.appendChild(make("li", "", step)));
        section.appendChild(list);
      }
      renderComparison(section, details.comparison_example);
      if (Array.isArray(details.audience_impacts)) {
        const list = make("div", "owner-audience-list");
        details.audience_impacts.forEach((impact) => {
          const row = make("div", "owner-audience-row");
          const statusLabel = {
            very_likely: "很可能有变化",
            possible: "可能有变化",
            not_observed: "目前没发现",
            unknown: "还没验证",
          }[impact.status] || "还没验证";
          append(row, make("strong", "", impact.audience), make("span", `owner-audience-state ${impact.status}`, statusLabel), make("span", "owner-audience-explanation", impact.explanation));
          list.appendChild(row);
        });
        section.appendChild(list);
      }
      if (Array.isArray(details.unknowns)) {
        const list = make("ul", "owner-simple-list");
        details.unknowns.forEach((unknown) => list.appendChild(make("li", "", unknown)));
        section.appendChild(list);
      }
      if (Array.isArray(details.owner_checks)) {
        const list = make("ol", "owner-check-list");
        details.owner_checks.forEach((check) => list.appendChild(make("li", "", check)));
        section.appendChild(list);
      }
      if (Array.isArray(details.actions) && details.actions.length) {
        const disclosure = make("details", "owner-action-details");
        disclosure.appendChild(make("summary", "", "查看详细验证步骤"));
        details.actions.forEach((action) => {
          const row = make("article", "owner-action-row");
          append(row, make("strong", "", action.title), make("p", "", action.instructions));
          disclosure.appendChild(row);
        });
        section.appendChild(disclosure);
      }
      const column = ["software_operation", "current_change"].includes(item.id)
        ? primaryColumn
        : secondaryColumn;
      column.appendChild(section);
    });
  }

  function ownerChangePresentation(node) {
    const changed = node?.change_state === "changed";
    const capability = ownerMapIsCapability();
    return {
      changed,
      eyebrow: changed ? (capability ? "AI 这次改了这项能力" : "AI 这次改了这里") : (capability ? "当前能力" : "当前工作步骤"),
      question: changed ? "这次改了什么" : (capability ? "这项能力变了吗" : "这次这里变了吗"),
      badge: changed ? "本次改动" : null,
    };
  }

  function ownerEvidenceBadge(node) {
    if (!node?.evidence_label) return null;
    const badge = make("span", `owner-evidence-badge ${node.evidence_status || "generated_candidate"}`, node.evidence_label);
    badge.title = node.evidence_note || node.evidence_label;
    return badge;
  }

  function ownerNodeBadges(node, changeBadge) {
    const evidenceBadge = ownerEvidenceBadge(node);
    if (!changeBadge && !evidenceBadge) return null;
    const badges = make("span", "owner-map-badges");
    if (changeBadge) badges.appendChild(make("span", "owner-change-badge", changeBadge));
    if (evidenceBadge) badges.appendChild(evidenceBadge);
    return badges;
  }

  function ownerMapData() {
    const map = softwareControl.working_map;
    return {nodes: map.overview_map.nodes, flows: map.overview_map.flows};
  }

  function ownerMapIsCapability() {
    return softwareControl?.working_map?.map_kind === "capability_map";
  }

  function ownerMappedDetails(overviewNode) {
    const nodesById = new Map(softwareControl.working_map.nodes.map((node) => [node.id, node]));
    return (overviewNode?.detail_node_ids || []).map((id) => nodesById.get(id)).filter(Boolean);
  }

  function ownerMappedFlows(detailNodes) {
    const detailIds = new Set(detailNodes.map((node) => node.id));
    return softwareControl.working_map.flows.filter((flow) => detailIds.has(flow.from) && detailIds.has(flow.to));
  }

  function ownerChangeLocation() {
    if (!softwareControl?.working_map?.overview_map) return null;
    const changedDetails = softwareControl.working_map.nodes.filter((node) => node.change_state === "changed");
    if (changedDetails.length !== 1) return null;
    const detail = changedDetails[0];
    const overviewMatches = softwareControl.working_map.overview_map.nodes.filter((node) =>
      (node.detail_node_ids || []).includes(detail.id),
    );
    if (overviewMatches.length !== 1) return null;
    return {overview: overviewMatches[0], detail};
  }

  function ownerRelationContext(node, nodes, flows) {
    if (ownerMapIsCapability()) {
      return {
        incoming: "这是并列能力之一；当前证据没有声明固定的前一步。",
        outgoing: "它可能被不同入口或其他能力组合使用；当前证据没有声明固定的后一步。",
      };
    }
    const labels = new Map(nodes.map((item) => [item.id, item.label]));
    const incoming = flows.filter((flow) => flow.to === node.id);
    const outgoing = flows.filter((flow) => flow.from === node.id);
    const relationCopy = (items, direction) => {
      if (!items.length) {
        return direction === "incoming"
          ? "按当前工作图，这是这一层流程的起点。"
          : "按当前工作图，这是这一层流程的终点。";
      }
      const names = [...new Set(items.map((flow) => labels.get(direction === "incoming" ? flow.from : flow.to)).filter(Boolean))];
      const relationLabels = [...new Set(items.map((flow) => flow.label).filter(Boolean))];
      if (window.PlainChangeI18n.locale === "en") {
        return `${direction === "incoming" ? "Previous step" : "Next step"}: ${names.join(", ")}${relationLabels.length ? `. Relationship: ${relationLabels.join(", ")}` : ""}.`;
      }
      const stepLabel = direction === "incoming" ? "前一步" : "后一步";
      const relationNote = relationLabels.length ? `；连接依据标为“${relationLabels.join("、")}”` : "";
      return `${stepLabel}：${names.map((name) => `「${name}」`).join("、")}${relationNote}。`;
    };
    return {
      incoming: relationCopy(incoming, "incoming"),
      outgoing: relationCopy(outgoing, "outgoing"),
    };
  }

  function ownerSystemFact(icon, title, text) {
    return append(
      make("article", "owner-system-fact"),
      make("span", "owner-system-fact-icon", icon),
      append(make("div", ""), make("h4", "", title), make("p", "", text)),
    );
  }

  function ownerSystemContext({responsibility, incoming, result, outgoing, change, evidence}) {
    const capability = ownerMapIsCapability();
    const section = make("section", "owner-system-context");
    append(
      section,
      ownerSystemFact("责", capability ? "这项能力负责什么" : "这个步骤负责什么", responsibility),
      ownerSystemFact("前", capability ? "它在结构中的位置" : "它从哪里来 / 前一步", incoming),
      ownerSystemFact("出", "它会产生什么", result),
      ownerSystemFact("后", capability ? "它可以怎样被使用" : "它会交给哪里 / 后一步", outgoing),
      ownerSystemFact("改", "这次修改发生在哪里", change),
      ownerSystemFact("据", "代码依据到哪里", evidence),
    );
    return section;
  }

  function ownerSecondaryContext(node, presentation) {
    const details = make("details", "owner-context-secondary");
    details.appendChild(make("summary", "", "查看变化影响与检查建议"));
    const body = make("div", "owner-context-secondary-body");
    append(
      body,
      detailRow("改", presentation.question, node.owner_view.current_change),
      detailRow("人", "谁可能受到影响", node.owner_view.affected_people),
    );
    const unknowns = make("section", "owner-inspector-section");
    unknowns.appendChild(make("h4", "", "仍然不知道"));
    const unknownList = make("ul", "owner-simple-list");
    node.owner_view.unknowns.forEach((item) => unknownList.appendChild(make("li", "", item)));
    append(unknowns, unknownList);
    const checks = make("section", "owner-inspector-section");
    checks.appendChild(make("h4", "", "你可以检查"));
    const checkList = make("ul", "owner-simple-list owner-checks");
    node.owner_view.owner_checks.forEach((item) => checkList.appendChild(make("li", "", item)));
    append(checks, checkList);
    append(body, unknowns, checks);
    details.appendChild(body);
    return details;
  }

  function ownerDetailElement(detailId) {
    return [...document.querySelectorAll("[data-owner-detail-id]")].find((node) => node.dataset.ownerDetailId === detailId) || null;
  }

  async function openOwnerChangeLocation() {
    const location = ownerChangeLocation();
    if (!location) return;
    state.ownerOverviewSelectedId = location.overview.id;
    state.ownerExpandedOverviewId = location.overview.id;
    state.ownerMapSelectedId = location.detail.id;
    await switchPage("architecture", false);
    window.requestAnimationFrame(() => window.requestAnimationFrame(() => {
      const target = ownerDetailElement(location.detail.id);
      if (!target) return;
      const arrivalLabel = make("span", "owner-arrival-label", "从变化页定位到这里");
      target.classList.add("owner-location-arrival");
      target.appendChild(arrivalLabel);
      const behavior = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
      target.scrollIntoView({block: "center", behavior});
      target.focus({preventScroll: true});
      showToast(`已定位到“${location.detail.label}”`);
      window.setTimeout(() => {
        target.classList.remove("owner-location-arrival");
        arrivalLabel.remove();
      }, 2600);
    }));
  }

  function computeOwnerMapLayout() {
    const map = ownerMapData();
    const nodes = map.nodes;
    if (ownerMapIsCapability()) {
      const columns = nodes.length === 1 ? 1 : 2;
      const placement = new Map();
      nodes.forEach((node, index) => {
        placement.set(node.id, {
          row: Math.floor(index / columns) + 1,
          column: index % columns + 1,
          span: 1,
        });
      });
      return {mode: "capability", nodes, placement, columns};
    }
    const byNode = new Map(nodes.map((node) => [node.id, node]));
    const pending = new Map(nodes.map((node) => [node.id, 0]));
    const outgoing = new Map(nodes.map((node) => [node.id, []]));
    map.flows.forEach((flow) => {
      pending.set(flow.to, pending.get(flow.to) + 1);
      outgoing.get(flow.from).push(flow.to);
    });
    const rank = new Map(nodes.map((node) => [node.id, 0]));
    const ready = nodes.filter((node) => pending.get(node.id) === 0);
    const ordered = [];
    while (ready.length) {
      const node = ready.shift();
      ordered.push(node);
      outgoing.get(node.id).forEach((target) => {
        rank.set(target, Math.max(rank.get(target), rank.get(node.id) + 1));
        pending.set(target, pending.get(target) - 1);
        if (pending.get(target) === 0) ready.push(byNode.get(target));
      });
    }
    if (ordered.length !== nodes.length) return {mode: "fallback", nodes, placement: new Map(), columns: 1};
    const groups = new Map();
    ordered.forEach((node) => {
      const row = rank.get(node.id);
      if (!groups.has(row)) groups.set(row, []);
      groups.get(row).push(node);
    });
    const columns = Math.max(1, ...[...groups.values()].map((group) => group.length));
    const placement = new Map();
    [...groups.entries()].sort((left, right) => left[0] - right[0]).forEach(([row, group]) => {
      group.forEach((node, index) => {
        const column = group.length === 1 ? 1 : Math.round(index * (columns - 1) / (group.length - 1)) + 1;
        placement.set(node.id, {row: row + 1, column, span: group.length === 1 ? columns : 1});
      });
    });
    return {mode: "graph", nodes: ordered, placement, columns};
  }

  function renderOwnerMapInspector() {
    const host = byId("owner-map-inspector");
    clear(host);
    host.removeAttribute("data-change-state");
    if (!state.ownerExpandedOverviewId) {
      const overviewNode = softwareControl.working_map.overview_map.nodes.find((item) => item.id === state.ownerOverviewSelectedId);
      if (!overviewNode) return;
      const presentation = ownerChangePresentation(overviewNode);
      const detailNodes = ownerMappedDetails(overviewNode);
      const canExpand = !ownerMapIsCapability() || detailNodes.length > 1;
      const changedDetail = detailNodes.find((item) => item.change_state === "changed");
      const relation = ownerRelationContext(
        overviewNode,
        softwareControl.working_map.overview_map.nodes,
        softwareControl.working_map.overview_map.flows,
      );
      const firstDetail = detailNodes[0];
      const lastDetail = detailNodes.at(-1);
      host.dataset.changeState = overviewNode.change_state;
      append(
        host,
        make("p", "eyebrow", presentation.changed ? (ownerMapIsCapability() ? "本次改动所在能力" : "本次改动所在阶段") : "当前系统位置"),
        make("h3", "", overviewNode.label),
        make("p", "owner-inspector-lead", overviewNode.description),
        ownerSystemContext({
          responsibility: overviewNode.description,
          incoming: relation.incoming,
          result: ownerMapIsCapability() && firstDetail
            ? firstDetail.owner_view.visible_result
            : firstDetail && lastDetail
            ? `按当前工作图，这个阶段从“${firstDetail.label}”推进到“${lastDetail.label}”。`
            : "当前工作图没有声明这个阶段更细的产出。",
          outgoing: relation.outgoing,
          change: changedDetail
            ? (ownerMapIsCapability() ? `本次修改定位在“${changedDetail.label}”这项能力。` : `本次修改定位在这个阶段中的“${changedDetail.label}”。`)
            : (ownerMapIsCapability() ? "当前证据没有把本次修改定位在这项能力。" : "当前证据没有把本次修改定位在这个阶段。"),
          evidence: `${window.PlainChangeI18n.translateText(overviewNode.evidence_label || "依据状态未标注")}: ${window.PlainChangeI18n.translateText(overviewNode.evidence_note || "当前工作图没有提供更具体的代码依据说明。")}`,
        }),
      );
      if (changedDetail) {
        host.appendChild(ownerSecondaryContext(changedDetail, ownerChangePresentation(changedDetail)));
      }
      const hint = make("div", "owner-overview-hint");
      append(
        hint,
        make("strong", "", ownerMapIsCapability()
          ? (canExpand ? `已识别 ${detailNodes.length} 项内部职责` : "暂未识别出更细的内部结构")
          : `这里包含 ${detailNodes.length} 个详细步骤`),
        make("p", "", ownerMapIsCapability()
          ? (canExpand ? "点击左侧能力，在全局结构中展开；再次点击即可收起。" : "当前证据只支持这一级，不会为了展示效果重复或编造子节点。")
          : "点击左侧这一步，在同一张图里展开详细过程。"),
      );
      host.appendChild(hint);
      return;
    }
    const node = softwareControl.working_map.nodes.find((item) => item.id === state.ownerMapSelectedId);
    if (!node) return;
    const presentation = ownerChangePresentation(node);
    const relation = ownerRelationContext(node, softwareControl.working_map.nodes, softwareControl.working_map.flows);
    host.dataset.changeState = node.change_state;
    append(
      host,
      make("p", "eyebrow", presentation.changed ? (ownerMapIsCapability() ? "本次改动所在能力" : "本次改动所在步骤") : "当前系统位置"),
      make("h3", "", node.label),
      make("p", "owner-inspector-lead", node.owner_view.meaning),
      ownerSystemContext({
        responsibility: node.owner_view.meaning,
        incoming: relation.incoming,
        result: node.owner_view.visible_result,
        outgoing: relation.outgoing,
        change: presentation.changed
          ? `本次修改定位在当前步骤。${node.owner_view.current_change}`
          : node.owner_view.current_change,
        evidence: `${window.PlainChangeI18n.translateText(node.evidence_label || "依据状态未标注")}: ${window.PlainChangeI18n.translateText(node.evidence_note || "当前工作图没有提供更具体的代码依据说明。")}`,
      }),
      ownerSecondaryContext(node, presentation),
    );
    if (node.implementation_group_ids.length) {
      host.appendChild(make("p", "owner-implementation-note", "技术实现已保留在下方，可按需展开核对。"));
    }
  }

  function drawOwnerMapLinks() {
    const svg = byId("owner-map-links");
    clear(svg);
    if (!softwareControl || ownerMapIsCapability() || state.page !== "architecture" || window.innerWidth <= 720 || state.ownerMapLayout?.mode === "fallback") return;
    const canvas = byId("owner-map-canvas");
    const canvasRect = canvas.getBoundingClientRect();
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("width", String(width));
    svg.setAttribute("height", String(height));
    const defs = makeSvg("defs");
    const marker = makeSvg("marker");
    marker.setAttribute("id", "owner-map-arrow");
    marker.setAttribute("viewBox", "0 0 10 10");
    marker.setAttribute("refX", "9");
    marker.setAttribute("refY", "5");
    marker.setAttribute("markerWidth", "7");
    marker.setAttribute("markerHeight", "7");
    marker.setAttribute("orient", "auto");
    const arrow = makeSvg("path", "owner-map-arrow-fill");
    arrow.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
    marker.appendChild(arrow);
    defs.appendChild(marker);
    svg.appendChild(defs);
    const boxFor = (id) => {
      const element = canvas.querySelector(`[data-owner-node-id="${id}"]`);
      if (!element) return null;
      const rect = element.getBoundingClientRect();
      return {
        left: rect.left - canvasRect.left,
        right: rect.right - canvasRect.left,
        top: rect.top - canvasRect.top,
        bottom: rect.bottom - canvasRect.top,
        centerX: rect.left - canvasRect.left + rect.width / 2,
        centerY: rect.top - canvasRect.top + rect.height / 2,
      };
    };
    const activeMap = ownerMapData();
    const boxes = new Map(activeMap.nodes.map((node) => [node.id, boxFor(node.id)]));
    const inlineObstacles = [...canvas.querySelectorAll(".owner-map-inline-details")].map((element) => {
      const rect = element.getBoundingClientRect();
      return {
        left: rect.left - canvasRect.left,
        right: rect.right - canvasRect.left,
        top: rect.top - canvasRect.top,
        bottom: rect.bottom - canvasRect.top,
        centerX: rect.left - canvasRect.left + rect.width / 2,
        centerY: rect.top - canvasRect.top + rect.height / 2,
      };
    });
    const obstacles = [...boxes.values(), ...inlineObstacles].filter(Boolean);
    const used = new Set();
    activeMap.flows.forEach((flow) => {
      const source = boxes.get(flow.from);
      const target = boxes.get(flow.to);
      if (!source || !target) return;
      const points = findTopDownConceptRoute(source, target, obstacles, width)
        || findOrthogonalConceptRoute(source, target, obstacles, width, height, used);
      if (!points) return;
      const path = makeSvg("path", "owner-map-link");
      path.dataset.from = flow.from;
      path.dataset.to = flow.to;
      path.setAttribute("d", `M ${points.map((point) => `${point.x} ${point.y}`).join(" L ")}`);
      path.setAttribute("marker-end", "url(#owner-map-arrow)");
      svg.appendChild(path);
    });
  }

  function renderOwnerMap() {
    const map = softwareControl.working_map;
    const activeMap = ownerMapData();
    const expandedOverview = map.overview_map.nodes.find((node) => node.id === state.ownerExpandedOverviewId) || null;
    const screen = map.screen_summary;
    byId("owner-map-headline").textContent = screen.headline;
    byId("owner-map-overview").textContent = screen.overview;
    byId("owner-map-state").textContent = screen.boundary_label;
    byId("owner-map-depth-label").textContent = expandedOverview
      ? (ownerMapIsCapability() ? `能力全景 · 已展开「${expandedOverview.label}」` : `四步总览 · 已展开「${expandedOverview.label}」`)
      : map.overview_map.title;
    byId("owner-map-back").textContent = ownerMapIsCapability() ? "收起当前能力" : "收起当前步骤";
    byId("owner-map-back").hidden = !expandedOverview;
    byId("owner-map-boundary").textContent = map.boundary_note;
    const evidenceKey = byId("owner-map-evidence-key");
    const hasDeclaredSource = map.nodes.some((node) => node.statement_state === "project_declared");
    const hasCodeLocation = map.nodes.some((node) => ["declared_and_code_supported", "partially_supported", "code_discovered", "model_interpreted_code_supported"].includes(node.evidence_status));
    const hasModelInterpretation = map.nodes.some((node) => ["model_interpreted_code_supported", "model_interpreted_only"].includes(node.evidence_status));
    evidenceKey.hidden = !hasDeclaredSource && !hasCodeLocation && !hasModelInterpretation;
    evidenceKey.querySelector('[data-evidence-key="declared"]').hidden = !hasDeclaredSource;
    evidenceKey.querySelector('[data-evidence-key="code"]').hidden = !hasCodeLocation;
    evidenceKey.querySelector('[data-evidence-key="model"]').hidden = !hasModelInterpretation;
    byId("owner-map-canvas").dataset.ownerMapState = expandedOverview ? "expanded" : "overview";
    byId("owner-map-canvas").dataset.ownerMapKind = ownerMapIsCapability() ? "capability" : "workflow";
    const layout = computeOwnerMapLayout();
    state.ownerMapLayout = layout;
    const host = byId("owner-map-nodes");
    clear(host);
    host.style.setProperty("--owner-map-columns", String(layout.columns));
    host.className = `owner-map-nodes ${layout.mode} overview${expandedOverview ? " has-expansion" : ""}`;
    layout.nodes.forEach((node, index) => {
      const presentation = ownerChangePresentation(node);
      const expanded = state.ownerExpandedOverviewId === node.id;
      const detailNodes = ownerMappedDetails(node);
      const canExpand = !ownerMapIsCapability() || detailNodes.length > 1;
      const group = make("section", `owner-map-overview-group${expanded ? " expanded" : ""}`);
      group.dataset.ownerOverviewGroupId = node.id;
      const button = make("button", `owner-map-node overview${node.change_state === "changed" ? " changed" : ""}${canExpand ? "" : " leaf"}`);
      button.type = "button";
      button.dataset.ownerNodeId = node.id;
      button.dataset.changeState = node.change_state;
      button.setAttribute("aria-pressed", String(state.ownerOverviewSelectedId === node.id));
      if (canExpand) {
        button.setAttribute("aria-expanded", String(expanded));
        button.setAttribute("aria-controls", `owner-inline-details-${node.id}`);
      }
      const placement = layout.placement.get(node.id);
      if (ownerMapIsCapability() && expanded) {
        group.style.gridColumn = "1 / -1";
      } else if (placement && !ownerMapIsCapability()) {
        group.style.gridColumn = placement.span > 1 ? `${placement.column} / span ${placement.span}` : String(placement.column);
        group.style.gridRow = String(placement.row);
      }
      const head = make("span", "owner-map-node-head");
      head.appendChild(make("span", "owner-map-number", ownerMapIsCapability() ? "◆" : String(index + 1).padStart(2, "0")));
      const copy = append(
        make("span", "owner-map-node-copy"),
        make("strong", "", node.label),
        make("span", "", node.description),
      );
      append(button, head, copy, ownerNodeBadges(node, presentation.badge));
      button.addEventListener("click", () => {
        if (!canExpand) {
          state.ownerOverviewSelectedId = node.id;
          state.ownerExpandedOverviewId = null;
          state.ownerMapSelectedId = detailNodes[0]?.id || state.ownerMapSelectedId;
          renderOwnerMap();
          document.querySelector(`[data-owner-node-id="${node.id}"]`)?.focus();
          return;
        }
        const collapsing = state.ownerExpandedOverviewId === node.id;
        state.ownerOverviewSelectedId = node.id;
        if (collapsing) {
          state.ownerExpandedOverviewId = null;
        } else {
          state.ownerMapSelectedId = detailNodes.find((item) => item.change_state === "changed")?.id
            || detailNodes[0]?.id
            || state.ownerMapSelectedId;
          state.ownerExpandedOverviewId = node.id;
        }
        renderOwnerMap();
        const focusSelector = collapsing
          ? `[data-owner-node-id="${node.id}"]`
          : `[data-owner-detail-id="${state.ownerMapSelectedId}"]`;
        document.querySelector(focusSelector)?.focus();
      });
      group.appendChild(button);
      if (expanded) {
        const detailNodes = ownerMappedDetails(node);
        const detailFlows = ownerMappedFlows(detailNodes);
        const detailLabels = new Map(detailNodes.map((item) => [item.id, item.label]));
        const panel = make("section", "owner-map-inline-details");
        panel.id = `owner-inline-details-${node.id}`;
        panel.setAttribute("aria-label", ownerMapIsCapability() ? `${node.label}的能力依据` : `${node.label}的详细过程`);
        const panelHeading = make("div", "owner-inline-heading");
        append(
          panelHeading,
          append(make("div", ""), make("strong", "", ownerMapIsCapability() ? "这项能力内部包含什么" : "这一步的详细过程"), make("span", "", "总览仍保留在这里")),
          make("span", "owner-inline-count", ownerMapIsCapability() ? `${detailNodes.length} 项依据` : `${detailNodes.length} 个步骤`),
        );
        panel.appendChild(panelHeading);
        const detailList = make("div", "owner-inline-detail-list");
        detailNodes.forEach((detailNode, detailIndex) => {
          const detailPresentation = ownerChangePresentation(detailNode);
          const detailButton = make("button", `owner-inline-detail ${detailNode.type}${detailNode.change_state === "changed" ? " changed" : ""}`);
          detailButton.type = "button";
          detailButton.dataset.ownerDetailId = detailNode.id;
          detailButton.dataset.changeState = detailNode.change_state;
          detailButton.setAttribute("aria-pressed", String(state.ownerMapSelectedId === detailNode.id));
          append(
            detailButton,
            make("span", "owner-inline-number", ownerMapIsCapability() ? "职" : String(detailIndex + 1).padStart(2, "0")),
            append(make("span", "owner-map-node-copy"), make("strong", "", detailNode.label), make("span", "", detailNode.owner_view.meaning)),
            ownerNodeBadges(detailNode, detailPresentation.badge),
          );
          detailButton.addEventListener("click", () => {
            state.ownerMapSelectedId = detailNode.id;
            renderOwnerMap();
            document.querySelector(`[data-owner-detail-id="${detailNode.id}"]`)?.focus();
          });
          detailList.appendChild(detailButton);
        });
        panel.appendChild(detailList);
        if (detailFlows.length) {
          const flowList = make("div", "owner-inline-flows");
          flowList.appendChild(make("strong", "", "这一步内部怎么连接"));
          detailFlows.forEach((flow) => {
            const row = make("span", "owner-inline-flow");
            append(row, make("span", "", `${detailLabels.get(flow.from)} → ${detailLabels.get(flow.to)}`), make("small", "", flow.label));
            flowList.appendChild(row);
          });
          panel.appendChild(flowList);
        }
        group.appendChild(panel);
      }
      host.appendChild(group);
    });
    const labels = new Map(activeMap.nodes.map((node) => [node.id, node.label]));
    const relationHost = byId("owner-map-relations");
    clear(relationHost);
    const relationDisclosure = document.querySelector(".owner-relation-disclosure");
    if (relationDisclosure) relationDisclosure.hidden = activeMap.flows.length === 0;
    activeMap.flows.forEach((flow) => {
      const row = make("div", "owner-map-relation");
      append(row, make("strong", "", `${labels.get(flow.from)} → ${labels.get(flow.to)}`), make("span", "", flow.label));
      relationHost.appendChild(row);
    });
    renderOwnerMapInspector();
    window.requestAnimationFrame(drawOwnerMapLinks);
  }

  function enableSoftwareControlUI() {
    if (!softwareControl) return;
    document.body.classList.add("software-control-mode");
    byId("owner-change").hidden = false;
    byId("owner-architecture").hidden = false;
    const legacyChange = byId("legacy-change-content");
    byId("legacy-change-host").appendChild(legacyChange);
    const legacyArchitecture = byId("legacy-architecture-content");
    byId("legacy-architecture-host").appendChild(legacyArchitecture);
    const implementationDisclosure = document.querySelector(".owner-implementation-disclosure");
    implementationDisclosure?.addEventListener("toggle", async () => {
      if (implementationDisclosure.open && await ensureArchitectureLoaded()) renderArchitecture();
    });
    renderOwnerStatus();
    renderAgentProvenance();
    renderOwnerQuestions();
    renderOwnerMap();
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
            sourceText("p", "", entry.text),
            entry.warning ? sourceText("small", "summary-context-warning", entry.warning) : null,
          );
          panel.appendChild(row);
        });
        panel.appendChild(make("p", "summary-context-rule", "判断顺序：用户明确提出 → AI 给出解释 → 用户是否确认。三种来源不能混为一谈。"));
        card.appendChild(panel);
      }
      host.appendChild(card);
    });
  }

  async function switchPage(nextPage, announce = false) {
    if (nextPage === "architecture" && !softwareControl && !(await ensureArchitectureLoaded())) {
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
      if (architecture) renderArchitecture();
      if (softwareControl) renderOwnerMap();
    }
    window.requestAnimationFrame(() => {
      window.scrollTo({top: state.pageScroll[nextPage] || 0, behavior: "auto"});
      if (nextPage === "architecture") {
        drawArchitectureLinks();
        drawOwnerMapLinks();
      }
    });
    if (announce) showToast(nextPage === "architecture" ? (softwareControl ? "已切换到这个软件怎么工作" : "已切换到整体架构") : (softwareControl ? "已切换到这次改了什么" : "已切换到变化解读"));
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

  function matchesModuleArea(rule, path) {
    const normalizedPath = path.toLowerCase();
    const filename = normalizedPath.split("/").at(-1) || "";
    return (rule.path_prefixes || []).some((prefix) => normalizedPath === String(prefix).toLowerCase()
      || normalizedPath.startsWith(`${String(prefix).replace(/\/$/, "").toLowerCase()}/`))
      || (rule.exact_paths || []).some((candidate) => normalizedPath === String(candidate).toLowerCase())
      || (rule.basename_prefixes || []).some((prefix) => filename.startsWith(String(prefix).toLowerCase()));
  }

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
      const rule = architectureModuleAreaRules.find((candidate) => matchesModuleArea(candidate, path)) || {
        id: `${group.group_id}-other`,
        order: 99,
        label: `其他${group.label}模块`,
        description: "未归入前述目录的模块，集中保留在这个阅读分组中。",
        source: "automatic_fallback",
      };
      if (!areas.has(rule.id)) {
        areas.set(rule.id, {
          ...rule,
          nodes: [],
          interfaceCount: 0,
          involvedCount: 0,
          source: rule.source || "target_profile",
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

  function architectureModuleAreaEdges(group, areas) {
    const groupNodeIds = new Set(group.node_ids);
    const areaForNode = new Map();
    areas.forEach((area) => area.nodes.forEach((node) => areaForNode.set(node.node_id, area.id)));
    const areasById = new Map(areas.map((area) => [area.id, area]));
    const aggregates = new Map();
    architectureEdges.forEach((edge) => {
      if (!groupNodeIds.has(edge.source_node_id) || !groupNodeIds.has(edge.target_node_id)) return;
      const sourceAreaId = areaForNode.get(edge.source_node_id);
      const targetAreaId = areaForNode.get(edge.target_node_id);
      if (!sourceAreaId || !targetAreaId || sourceAreaId === targetAreaId) return;
      const key = `${sourceAreaId}|${targetAreaId}`;
      if (!aggregates.has(key)) {
        aggregates.set(key, {
          source: areasById.get(sourceAreaId),
          target: areasById.get(targetAreaId),
          edgeIds: [],
        });
      }
      aggregates.get(key).edgeIds.push(edge.edge_id);
    });
    return [...aggregates.values()]
      .map((edge) => ({...edge, edgeIds: edge.edgeIds.sort()}))
      .sort((left, right) => right.edgeIds.length - left.edgeIds.length || left.source.id.localeCompare(right.source.id) || left.target.id.localeCompare(right.target.id));
  }

  function conceptTypeLabel(type) {
    return {
      input: "外部输入",
      process: "自动处理",
      output: "可读输出",
      human_gate: "人工决定",
      state: "持久状态",
    }[type] || "系统组件";
  }

  function selectImplementationGroup(groupId) {
    if (!architectureGroups.has(groupId)) {
      showToast("这项概念在当前静态快照中没有可下钻的代码分区");
      return;
    }
    state.architectureSelectedGroup = groupId;
    state.architectureSelectedRelation = null;
    state.architectureSelectedNode = null;
    state.architectureSelectedArea = null;
    state.architectureModuleDetailsOpen = false;
    state.architectureModuleLimit = 18;
    renderArchitecture();
  }

  function compareConceptComponents(left, right) {
    return left.grid_column - right.grid_column || left.grid_row - right.grid_row || left.id.localeCompare(right.id);
  }

  function computeConceptualLayout() {
    const components = conceptualArchitecture.components.slice().sort(compareConceptComponents);
    const componentById = new Map(components.map((component) => [component.id, component]));
    const pending = new Map(components.map((component) => [component.id, 0]));
    const outgoing = new Map(components.map((component) => [component.id, []]));
    conceptualArchitecture.flows.forEach((flow) => {
      pending.set(flow.to, (pending.get(flow.to) || 0) + 1);
      outgoing.get(flow.from)?.push(flow.to);
    });
    const rank = new Map(components.map((component) => [component.id, 0]));
    const ready = components.filter((component) => pending.get(component.id) === 0).sort(compareConceptComponents);
    const ordered = [];
    while (ready.length) {
      const component = ready.shift();
      ordered.push(component);
      (outgoing.get(component.id) || []).forEach((targetId) => {
        rank.set(targetId, Math.max(rank.get(targetId) || 0, (rank.get(component.id) || 0) + 1));
        pending.set(targetId, (pending.get(targetId) || 0) - 1);
        if (pending.get(targetId) === 0) {
          ready.push(componentById.get(targetId));
          ready.sort(compareConceptComponents);
        }
      });
    }
    if (ordered.length !== components.length) {
      return {
        mode: "fallback",
        reason: "关系包含循环，已切换为结构化阅读；下方保留全部关系说明。",
        components,
        placement: new Map(),
        columns: 1,
        isLinear: false,
      };
    }
    const rankGroups = new Map();
    ordered.forEach((component) => {
      const value = rank.get(component.id) || 0;
      if (!rankGroups.has(value)) rankGroups.set(value, []);
      rankGroups.get(value).push(component);
    });
    rankGroups.forEach((group) => group.sort(compareConceptComponents));
    const rankedRows = [...rankGroups.keys()].sort((left, right) => left - right);
    const tracks = Math.max(...rankedRows.map((value) => rankGroups.get(value).length));
    const placement = new Map();
    rankedRows.forEach((value, rowIndex) => {
      const group = rankGroups.get(value);
      group.forEach((component, index) => {
        const column = group.length === 1
          ? 1
          : Math.round(index * (tracks - 1) / (group.length - 1)) + 1;
        placement.set(component.id, {
          column,
          row: rowIndex + 1,
          span: group.length === 1 ? tracks : 1,
        });
      });
    });
    const rows = rankedRows.length;
    const sources = rankGroups.get(0)?.length || 0;
    const isLinear = sources <= 2 && [...rankGroups.entries()].every(([value, group]) => value === 0 || group.length === 1);
    return {
      mode: isLinear ? "story" : "layered",
      reason: isLinear ? "" : "该图包含分支或汇合，已按关系层级排布；下方保留全部关系说明。",
      components: ordered.slice().sort((left, right) => {
        const leftPlacement = placement.get(left.id);
        const rightPlacement = placement.get(right.id);
        return leftPlacement.row - rightPlacement.row || leftPlacement.column - rightPlacement.column || compareConceptComponents(left, right);
      }),
      placement,
      columns: tracks,
      rows,
      isLinear,
    };
  }

  function renderConceptualArchitecture() {
    const host = byId("architecture-concept");
    if (!conceptualArchitecture) {
      host.hidden = true;
      return;
    }
    host.hidden = false;
    byId("architecture-concept-title").textContent = conceptualArchitecture.title;
    byId("architecture-concept-description").textContent = conceptualArchitecture.description;
    byId("architecture-concept-boundary").textContent = conceptualArchitecture.boundary_note;
    byId("architecture-concept-source").textContent = `${conceptualArchitecture.source.label} · ${conceptualArchitecture.source.profile_id}`;

    const layoutPlan = computeConceptualLayout();
    state.conceptLayout = layoutPlan;
    const components = layoutPlan.components;
    const inputs = components.filter((component) => component.type === "input");
    const stageNumber = new Map(components.map((component, index) => [component.id, index + 1]));
    const canvas = byId("architecture-concept-canvas");
    const layoutStatus = byId("architecture-concept-layout-status");
    canvas.dataset.conceptLayout = layoutPlan.mode;
    layoutStatus.hidden = !layoutPlan.reason;
    layoutStatus.textContent = layoutPlan.reason;
    const grid = byId("architecture-concept-components");
    grid.className = `architecture-concept-components ${layoutPlan.mode}`;
    grid.style.setProperty("--concept-tracks", String(Math.max(1, layoutPlan.columns)));
    clear(grid);
    components.forEach((component) => {
      const directGroup = component.implementation_groups.length === 1
        ? component.implementation_groups[0]
        : null;
      const card = make("button", `concept-component ${component.type}`);
      card.dataset.conceptId = component.id;
      card.type = "button";
      const directSelectionActive = Boolean(
        directGroup
        && state.architectureSelectedConcept === component.id
        && state.architectureSelectedGroup === directGroup.id,
      );
      card.setAttribute("aria-pressed", String(
        directGroup
          ? directSelectionActive
          : state.architectureSelectedConcept === component.id,
      ));
      if (directGroup) {
        card.setAttribute("aria-expanded", String(directSelectionActive));
      }
      card.addEventListener("click", () => {
        if (directGroup && directSelectionActive) {
          state.architectureSelectedConcept = null;
          state.architectureSelectedGroup = null;
          state.architectureSelectedArea = null;
          state.architectureSelectedNode = null;
          state.architectureSelectedRelation = null;
          renderArchitecture();
          return;
        }
        state.architectureSelectedConcept = component.id;
        if (directGroup) {
          selectImplementationGroup(directGroup.id);
        } else {
          state.architectureSelectedGroup = null;
          state.architectureSelectedArea = null;
          state.architectureSelectedNode = null;
          renderArchitecture();
        }
      });
      if (directGroup) {
        card.dataset.groupId = directGroup.id;
      }
      const placement = layoutPlan.placement.get(component.id) || {column: 1, row: 1, span: 1};
      if (layoutPlan.mode !== "fallback") {
        card.style.gridColumn = placement.span > 1
          ? `${placement.column} / span ${placement.span}`
          : String(placement.column);
        card.style.gridRow = String(placement.row);
      }
      const head = make("div", "concept-component-head");
      const marker = make("span", "concept-stage", String(stageNumber.get(component.id)).padStart(2, "0"));
      append(head, marker, make("h4", "", component.label), make("span", "concept-type", conceptTypeLabel(component.type)));
      append(card, head, make("p", "", component.description));
      if (component.implementation_groups.length) {
        const mapping = make("div", "concept-implementation");
        const implementationSeparator = window.PlainChangeI18n.locale === "en" ? ", " : "、";
        mapping.textContent = directGroup
          ? `点击展开：${directGroup.label}`
          : `对应实现：${component.implementation_groups.map((item) => item.label).join(implementationSeparator)}`;
        card.appendChild(mapping);
        if (!directGroup) card.appendChild(make("span", "concept-unmapped", "一个工作步骤可能对应多个实现分区；请在右侧核对。"));
      } else if (component.type === "human_gate") {
        card.appendChild(make("span", "concept-unmapped", "这一步在系统外部，由人明确决定"));
      } else {
        card.appendChild(make("span", "concept-unmapped", "外部输入或状态，不映射为单一代码分区"));
      }
      if (directGroup) card.appendChild(make("span", "concept-expanded-label", "实现已展开"));
      grid.appendChild(card);
    });

    const componentLabels = new Map(components.map((item) => [item.id, item.label]));
    const relationHost = byId("architecture-concept-relations");
    clear(relationHost);
    const isInputFlow = (flow) => inputs.some((component) => component.id === flow.from);
    [
      {title: layoutPlan.isLinear ? "主路径（按编号阅读）" : "关系说明（按层阅读）", flows: conceptualArchitecture.flows.filter((flow) => !isInputFlow(flow))},
      {title: "输入如何进入主干", flows: conceptualArchitecture.flows.filter(isInputFlow)},
    ].forEach((group) => {
      if (!group.flows.length) return;
      const section = make("section", "architecture-concept-relation-group");
      const list = make("div", "architecture-concept-relation-list");
      group.flows.forEach((flow) => {
        const row = make("div", "architecture-concept-relation");
        append(
          row,
          make("strong", "", `${componentLabels.get(flow.from) || flow.from} → ${componentLabels.get(flow.to) || flow.to}`),
          make("span", "", flow.label),
        );
        list.appendChild(row);
      });
      append(section, make("h4", "", group.title), list);
      relationHost.appendChild(section);
    });
  }

  function routeKey(left, right) {
    const first = `${left.x},${left.y}`;
    const second = `${right.x},${right.y}`;
    return first < second ? `${first}|${second}` : `${second}|${first}`;
  }

  function compressOrthogonalPoints(points) {
    const deduped = points.filter((point, index) => index === 0 || point.x !== points[index - 1].x || point.y !== points[index - 1].y);
    return deduped.filter((point, index) => {
      if (index === 0 || index === deduped.length - 1) return true;
      const previous = deduped[index - 1];
      const next = deduped[index + 1];
      return !((previous.x === point.x && point.x === next.x) || (previous.y === point.y && point.y === next.y));
    });
  }

  function findOrthogonalConceptRoute(source, target, obstacles, width, height, usedSegments) {
    const margin = 14;
    const portsFor = (box) => [
      {x: box.left - margin, y: box.centerY, edge: {x: box.left, y: box.centerY}},
      {x: box.right + margin, y: box.centerY, edge: {x: box.right, y: box.centerY}},
      {x: box.centerX, y: box.top - margin, edge: {x: box.centerX, y: box.top}},
      {x: box.centerX, y: box.bottom + margin, edge: {x: box.centerX, y: box.bottom}},
    ];
    const sourcePorts = portsFor(source);
    const targetPorts = portsFor(target);
    const xs = new Set([margin, Math.max(margin, width - margin)]);
    const ys = new Set([margin, Math.max(margin, height - margin)]);
    obstacles.forEach((box) => {
      [box.left - margin, box.left, box.right, box.right + margin].forEach((value) => xs.add(Math.max(margin, Math.min(width - margin, value))));
      [box.top - margin, box.top, box.bottom, box.bottom + margin].forEach((value) => ys.add(Math.max(margin, Math.min(height - margin, value))));
    });
    [...sourcePorts, ...targetPorts].forEach((port) => {
      xs.add(port.x);
      ys.add(port.y);
    });
    const xValues = [...xs].sort((left, right) => left - right);
    const yValues = [...ys].sort((left, right) => left - right);
    const key = (x, y) => `${x},${y}`;
    const expanded = obstacles
      .filter((box) => box !== source && box !== target)
      .map((box) => ({left: box.left - margin, right: box.right + margin, top: box.top - margin, bottom: box.bottom + margin}));
    const pointBlocked = (point) => expanded.some((box) => point.x > box.left && point.x < box.right && point.y > box.top && point.y < box.bottom);
    const segmentBlocked = (left, right) => expanded.some((box) => {
      if (left.y === right.y) {
        return left.y > box.top && left.y < box.bottom && Math.max(left.x, right.x) > box.left && Math.min(left.x, right.x) < box.right;
      }
      return left.x > box.left && left.x < box.right && Math.max(left.y, right.y) > box.top && Math.min(left.y, right.y) < box.bottom;
    });
    const coordinates = new Map();
    xValues.forEach((x) => yValues.forEach((y) => {
      const point = {x, y};
      if (!pointBlocked(point)) coordinates.set(key(x, y), point);
    }));
    const targetPortByKey = new Map(targetPorts.map((port) => [key(port.x, port.y), port]));
    const sourcePortByKey = new Map(sourcePorts.map((port) => [key(port.x, port.y), port]));
    const distance = new Map();
    const previous = new Map();
    const queue = [];
    sourcePortByKey.forEach((port, portKey) => {
      if (!coordinates.has(portKey)) return;
      distance.set(portKey, 0);
      queue.push(portKey);
    });
    let matchedTarget = null;
    while (queue.length) {
      queue.sort((left, right) => (distance.get(left) || Infinity) - (distance.get(right) || Infinity));
      const currentKey = queue.shift();
      if (targetPortByKey.has(currentKey)) {
        matchedTarget = currentKey;
        break;
      }
      const current = coordinates.get(currentKey);
      const xIndex = xValues.indexOf(current.x);
      const yIndex = yValues.indexOf(current.y);
      [[xValues[xIndex - 1], current.y], [xValues[xIndex + 1], current.y], [current.x, yValues[yIndex - 1]], [current.x, yValues[yIndex + 1]]]
        .filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y))
        .forEach(([x, y]) => {
          const nextKey = key(x, y);
          const next = coordinates.get(nextKey);
          if (!next || segmentBlocked(current, next)) return;
          const segment = routeKey(current, next);
          const candidate = (distance.get(currentKey) || 0) + Math.abs(current.x - next.x) + Math.abs(current.y - next.y) + (usedSegments.has(segment) ? 2000 : 0);
          if (candidate >= (distance.get(nextKey) ?? Infinity)) return;
          distance.set(nextKey, candidate);
          previous.set(nextKey, currentKey);
          queue.push(nextKey);
        });
    }
    if (!matchedTarget) return null;
    const routeKeys = [];
    for (let currentKey = matchedTarget; currentKey; currentKey = previous.get(currentKey)) routeKeys.unshift(currentKey);
    const sourcePort = sourcePortByKey.get(routeKeys[0]);
    const targetPort = targetPortByKey.get(matchedTarget);
    const points = compressOrthogonalPoints([sourcePort.edge, ...routeKeys.map((item) => coordinates.get(item)), targetPort.edge]);
    for (let index = 1; index < routeKeys.length; index += 1) usedSegments.add(routeKey(coordinates.get(routeKeys[index - 1]), coordinates.get(routeKeys[index])));
    return points;
  }

  function routeCrossesConceptCard(points, obstacles, source, target) {
    return points.slice(1).some((point, index) => {
      const previous = points[index];
      return obstacles.some((box) => {
        if (box === source || box === target) return false;
        if (previous.y === point.y) {
          return previous.y > box.top && previous.y < box.bottom
            && Math.max(previous.x, point.x) > box.left && Math.min(previous.x, point.x) < box.right;
        }
        return previous.x > box.left && previous.x < box.right
          && Math.max(previous.y, point.y) > box.top && Math.min(previous.y, point.y) < box.bottom;
      });
    });
  }

  function findTopDownConceptRoute(source, target, obstacles, width) {
    if (target.top <= source.bottom) return null;
    const start = {x: source.centerX, y: source.bottom};
    const end = {x: target.centerX, y: target.top};
    const middleY = (start.y + end.y) / 2;
    const direct = Math.abs(start.x - end.x) < 4
      ? [start, end]
      : [start, {x: start.x, y: middleY}, {x: end.x, y: middleY}, end];
    if (!routeCrossesConceptCard(direct, obstacles, source, target)) return direct;
    const margin = 12;
    const sourceGutterY = source.bottom + margin;
    const targetGutterY = target.top - margin;
    const sideRoutes = [margin, Math.max(margin, width - margin)].map((gutterX) => [
      start,
      {x: start.x, y: sourceGutterY},
      {x: gutterX, y: sourceGutterY},
      {x: gutterX, y: targetGutterY},
      {x: end.x, y: targetGutterY},
      end,
    ]);
    return sideRoutes.find((points) => !routeCrossesConceptCard(points, obstacles, source, target)) || null;
  }

  function drawConceptualLinks() {
    const svg = byId("architecture-concept-links");
    clear(svg);
    if (!conceptualArchitecture || state.page !== "architecture" || window.innerWidth <= 720 || state.conceptLayout?.mode === "fallback") return;
    const canvas = byId("architecture-concept-canvas");
    const canvasRect = canvas.getBoundingClientRect();
    const width = Math.max(canvas.scrollWidth, canvas.clientWidth);
    const height = Math.max(canvas.scrollHeight, canvas.clientHeight);
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("width", String(width));
    svg.setAttribute("height", String(height));
    const defs = makeSvg("defs");
    ["system", "human"].forEach((kind) => {
      const marker = makeSvg("marker");
      marker.setAttribute("id", `architecture-concept-arrow-${kind}`);
      marker.setAttribute("viewBox", "0 0 10 10");
      marker.setAttribute("refX", "9");
      marker.setAttribute("refY", "5");
      marker.setAttribute("markerWidth", "7");
      marker.setAttribute("markerHeight", "7");
      marker.setAttribute("orient", "auto");
      const markerPath = makeSvg("path", `architecture-concept-arrow-fill${kind === "human" ? " human" : ""}`);
      markerPath.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
      marker.appendChild(markerPath);
      defs.appendChild(marker);
    });
    svg.appendChild(defs);
    const componentIndex = new Map(conceptualArchitecture.components.map((item) => [item.id, item]));
    const box = (id) => {
      const node = canvas.querySelector(`[data-concept-id="${id}"]`);
      if (!node) return null;
      const rect = node.getBoundingClientRect();
      return {
        left: rect.left - canvasRect.left + canvas.scrollLeft,
        right: rect.right - canvasRect.left + canvas.scrollLeft,
        top: rect.top - canvasRect.top + canvas.scrollTop,
        bottom: rect.bottom - canvasRect.top + canvas.scrollTop,
        centerX: rect.left - canvasRect.left + canvas.scrollLeft + rect.width / 2,
        centerY: rect.top - canvasRect.top + canvas.scrollTop + rect.height / 2,
      };
    };
    const componentBoxes = new Map(conceptualArchitecture.components.map((component) => [component.id, box(component.id)]));
    const obstacles = [...componentBoxes.values()].filter(Boolean);
    const usedSegments = new Set();
    const routes = conceptualArchitecture.flows.map((flow) => {
      const source = componentBoxes.get(flow.from);
      const target = componentBoxes.get(flow.to);
      if (!source || !target) return {flow, points: null};
      const points = findTopDownConceptRoute(source, target, obstacles, width)
        || findOrthogonalConceptRoute(source, target, obstacles, width, height, usedSegments);
      return {flow, points};
    });
    if (routes.some(({points}) => !points)) {
      clear(svg);
      canvas.dataset.conceptLayout = "fallback";
      const grid = byId("architecture-concept-components");
      grid.className = "architecture-concept-components fallback";
      grid.querySelectorAll(".concept-component").forEach((card) => {
        card.style.gridColumn = "";
        card.style.gridRow = "";
      });
      state.conceptLayout = {...state.conceptLayout, mode: "fallback"};
      const layoutStatus = byId("architecture-concept-layout-status");
      layoutStatus.hidden = false;
      layoutStatus.textContent = "关系过于密集，已切换为结构化阅读；下方保留全部关系说明。";
      return;
    }
    routes.forEach(({flow, points}) => {
      const human = componentIndex.get(flow.to)?.type === "human_gate" || componentIndex.get(flow.from)?.type === "human_gate";
      const path = makeSvg("path", `architecture-concept-link${human ? " human" : ""}`);
      path.dataset.from = flow.from;
      path.dataset.to = flow.to;
      path.setAttribute("d", `M ${points.map((point) => `${point.x} ${point.y}`).join(" L ")}`);
      path.setAttribute("marker-end", `url(#architecture-concept-arrow-${human ? "human" : "system"})`);
      svg.appendChild(path);
    });
  }

  function renderArchitectureHeader() {
    const coverage = architecture.coverage;
    byId("architecture-description").textContent = conceptualArchitecture
      ? "先通过系统工作流理解输入、处理、输出和人工边界；再向下核对冻结源码的静态实现。"
      : "当前配置没有声明系统工作流；以下仅展示冻结源码中的静态代码结构。";
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
    const stage = byId("architecture-implementation");
    clear(host);
    const selectedGroup = architectureGroups.get(state.architectureSelectedGroup);
    const showStaticOverview = !conceptualArchitecture;
    stage.hidden = !selectedGroup && !showStaticOverview;
    if (!selectedGroup) {
      if (showStaticOverview) architecture.groups.forEach((group) => host.appendChild(architectureGroupButton(group)));
      return;
    }
    const nodes = selectedGroup.node_ids.map((nodeId) => architectureNodes.get(nodeId)).filter(Boolean);
    const areas = architectureModuleAreas(selectedGroup, nodes);
    const selectedArea = areas.find((area) => area.id === state.architectureSelectedArea) || null;
    const areaEdges = architectureModuleAreaEdges(selectedGroup, areas);
    const edgeCountByArea = new Map(areas.map((area) => [area.id, {incoming: 0, outgoing: 0}]));
    areaEdges.forEach((edge) => {
      edgeCountByArea.get(edge.source.id).outgoing += edge.edgeIds.length;
      edgeCountByArea.get(edge.target.id).incoming += edge.edgeIds.length;
    });
    const expanded = make("section", "architecture-inline-expansion");
    append(
      expanded,
      append(
        make("div", "architecture-inline-heading"),
        make("p", "eyebrow", "展开的静态实现"),
        make("h3", "", selectedGroup.label),
        make("p", "", "下列子域由目标配置归类；关系仅汇总当前冻结源码中已有的静态 import。"),
      ),
      make("p", "architecture-inline-boundary", "这不是运行时调用顺序。动态注入、网络、数据库和部署关系仍需要独立证据。"),
    );
    const cards = make("div", "implementation-subdomain-card-grid architecture-inline-subdomains");
    areas.forEach((area, index) => {
      const counts = edgeCountByArea.get(area.id);
      const card = make("button", "implementation-subdomain-card");
      card.type = "button";
      card.dataset.subdomainId = area.id;
      card.setAttribute("aria-pressed", String(selectedArea?.id === area.id));
      append(
        card,
        make("span", "implementation-subdomain-number", String(index + 1).padStart(2, "0")),
        append(make("span", "implementation-subdomain-copy"), make("strong", "", area.label), make("span", "", area.description)),
        append(
          make("span", "implementation-subdomain-meta"),
          make("span", "", `${area.nodes.length} 模块`),
          make("span", "", `入 ${counts.incoming} / 出 ${counts.outgoing}`),
          area.involvedCount ? make("span", "involved", `本次涉及 ${area.involvedCount}`) : null,
        ),
      );
      card.addEventListener("click", () => {
        state.architectureSelectedArea = state.architectureSelectedArea === area.id ? null : area.id;
        state.architectureSelectedNode = null;
        state.architectureModuleDetailsOpen = false;
        state.architectureModuleLimit = 18;
        renderArchitecture();
      });
      cards.appendChild(card);
    });
    expanded.appendChild(cards);
    const relations = make("div", "implementation-subdomain-relations");
    if (!areaEdges.length) {
      relations.appendChild(make("p", "technical-note", "当前快照没有跨子域静态 import；每个子域内部关系仍可在右侧按需核对。"));
    } else {
      areaEdges.forEach((edge) => {
        const row = make("div", "implementation-subdomain-relation");
        append(row, make("strong", "", `${edge.source.label} → ${edge.target.label}`), make("span", "", `${edge.edgeIds.length} 条静态 import`));
        relations.appendChild(row);
      });
    }
    expanded.appendChild(relations);
    host.appendChild(expanded);
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
    if (!svg) return;
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
    const concept = conceptualArchitecture?.components.find((item) => item.id === state.architectureSelectedConcept) || null;
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
      });
      host.appendChild(back);
      return;
    }
    if (!group) {
      if (concept) {
        append(
          host,
          make("p", "eyebrow", "当前工作步骤"),
          make("h3", "", concept.label),
          make("p", "", concept.description),
        );
        if (concept.implementation_groups.length > 1) {
          host.appendChild(make("p", "technical-note", "这一步对应多个静态分区；请选择一个实现分区继续查看。"));
          const choices = make("div", "architecture-actions");
          concept.implementation_groups.forEach((mapped) => {
            const button = make("button", "secondary-button", mapped.label);
            button.type = "button";
            button.addEventListener("click", () => selectImplementationGroup(mapped.id));
            choices.appendChild(button);
          });
          host.appendChild(choices);
        } else {
          host.appendChild(make("p", "technical-note", concept.type === "human_gate"
            ? "这是系统外部的人工决定，不映射为代码分区。"
            : "这是外部输入或状态，不映射为单一代码分区。"));
        }
        return;
      }
      append(
        host,
        make("p", "eyebrow", "系统全景"),
        make("h3", "", "从工作流进入实现"),
        make("p", "", "在左侧图中点击有“点击展开”提示的工作步骤，静态实现会直接在同一张图中展开。"),
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
    const nodes = group.node_ids.map((nodeId) => architectureNodes.get(nodeId)).filter(Boolean);
    const areas = architectureModuleAreas(group, nodes);
    const selectedArea = areas.find((area) => area.id === state.architectureSelectedArea) || null;
    if (selectedArea) {
      const areaEdges = architectureModuleAreaEdges(group, areas)
        .filter((edge) => edge.source.id === selectedArea.id || edge.target.id === selectedArea.id);
      append(
        host,
        make("p", "eyebrow", "当前实现子域"),
        make("h3", "", selectedArea.label),
        make("p", "", selectedArea.description),
      );
      const facts = make("div", "facts-grid");
      append(
        facts,
        fact("所属分区", group.label),
        fact("包含模块", `${selectedArea.nodes.length} 个`),
        fact("对外入口", `${selectedArea.interfaceCount} 个`),
        fact("本次变化", `${selectedArea.involvedCount} 个`),
        fact("分组依据", selectedArea.source === "target_profile" ? "目标配置规则" : "自动候选"),
      );
      host.appendChild(facts);
      const relations = make("section", "architecture-direct-relations");
      append(relations, make("h4", "", "与其他实现子域的静态关系"), make("p", "architecture-relation-help", "每一项都聚合已有静态 import；它不代表运行时调用。"));
      if (!areaEdges.length) {
        relations.appendChild(make("p", "technical-note", "当前没有跨实现子域的静态 import。"));
      } else {
        const list = make("div", "architecture-direct-list");
        areaEdges.forEach((edge) => {
          const direction = edge.source.id === selectedArea.id ? "依赖 →" : "← 被依赖";
          const other = edge.source.id === selectedArea.id ? edge.target : edge.source;
          const row = make("div", "architecture-direct-relation");
          append(row, make("span", "relation-direction", direction), make("strong", "", other.label), make("span", "relation-count", `${edge.edgeIds.length} 条`));
          list.appendChild(row);
        });
        relations.appendChild(list);
      }
      host.appendChild(relations);
      const source = make("details", "architecture-module-details");
      source.appendChild(make("summary", "", `按需核对 ${selectedArea.nodes.length} 个技术模块`));
      const list = make("div", "architecture-inspector-module-list");
      selectedArea.nodes.slice(0, state.architectureModuleLimit).forEach((item) => {
        const button = make("button", "module-card");
        button.type = "button";
        append(button, make("strong", "", architectureNodeLabel(item)), make("span", "", item.owned_paths?.[0] || item.label));
        button.addEventListener("click", () => {
          state.architectureSelectedNode = item.node_id;
          renderArchitectureInspector();
        });
        list.appendChild(button);
      });
      source.appendChild(list);
      host.appendChild(source);
      return;
    }
    append(
      host,
      make("p", "eyebrow", "当前静态实现分区"),
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
      fact("分区来源", group.group_id === "unclassified" ? "待人工归类" : "目标配置"),
    );
    host.appendChild(facts);
    renderArchitectureDirectRelations(host, group);
    const actions = make("div", "architecture-actions");
    const close = make("button", "secondary-button", "收起当前实现");
    close.type = "button";
    close.addEventListener("click", () => {
      state.architectureSelectedGroup = null;
      state.architectureSelectedConcept = null;
      state.architectureSelectedRelation = null;
      state.architectureSelectedNode = null;
      state.architectureSelectedArea = null;
      state.architectureModuleDetailsOpen = false;
      renderArchitecture();
    });
    actions.appendChild(close);
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
      make("p", "", `先从 ${areas.length} 个实现子域理解结构；只有需要核对时，才展开具体源码模块。`),
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
      ["2", "实现子域", selectedArea ? selectedArea.label : "请先选择", selectedArea ? "done" : "active"],
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
    host.appendChild(make("p", "module-layer-note", "实现子域优先按目标配置规则匹配；未命中的模块会明确归入“其他”。子域关系只汇总已有静态 import，不代表运行时先后顺序。"));

    const areaEdges = architectureModuleAreaEdges(group, areas);
    const edgeCountByArea = new Map(areas.map((area) => [area.id, {incoming: 0, outgoing: 0}]));
    areaEdges.forEach((edge) => {
      edgeCountByArea.get(edge.source.id).outgoing += edge.edgeIds.length;
      edgeCountByArea.get(edge.target.id).incoming += edge.edgeIds.length;
    });
    const subdomainMap = make("section", "implementation-subdomain-map");
    const mapHead = make("div", "implementation-subdomain-map-head");
    append(
      mapHead,
      append(
        make("div", ""),
        make("p", "eyebrow", "第 2 层 · 实现子域图"),
        make("h4", "", `${group.label}由哪些实现部分组成`),
        make("p", "", "每张卡是一个可审计的源码子域；箭头文字汇总子域之间已有的静态 import，而不是运行时调用。"),
      ),
      make("span", "implementation-subdomain-map-source", areas.some((area) => area.source === "target_profile") ? "目标配置优先" : "自动候选"),
    );
    subdomainMap.appendChild(mapHead);
    const mapCards = make("div", "implementation-subdomain-card-grid");
    areas.forEach((area, index) => {
      const counts = edgeCountByArea.get(area.id);
      const button = make("button", "implementation-subdomain-card");
      button.type = "button";
      button.dataset.subdomainId = area.id;
      button.setAttribute("aria-pressed", String(selectedArea?.id === area.id));
      append(
        button,
        make("span", "implementation-subdomain-number", String(index + 1).padStart(2, "0")),
        append(make("span", "implementation-subdomain-copy"), make("strong", "", area.label), make("span", "", area.description)),
        append(
          make("span", "implementation-subdomain-meta"),
          make("span", "", `${area.nodes.length} 模块`),
          make("span", "", `入 ${counts.incoming} / 出 ${counts.outgoing}`),
          area.involvedCount ? make("span", "involved", `本次涉及 ${area.involvedCount}`) : null,
        ),
      );
      button.addEventListener("click", () => {
        state.architectureSelectedArea = area.id;
        state.architectureSelectedNode = null;
        state.architectureModuleDetailsOpen = false;
        state.architectureModuleLimit = 18;
        renderArchitectureInspector();
        renderArchitectureModules();
        showToast(`已选择${area.label}`);
      });
      mapCards.appendChild(button);
    });
    subdomainMap.appendChild(mapCards);
    const mapRelations = make("div", "implementation-subdomain-relations");
    if (!areaEdges.length) {
      mapRelations.appendChild(make("p", "technical-note", "当前快照没有跨实现子域的静态 import；每个子域内部关系仍可在模块层核对。"));
    } else {
      areaEdges.forEach((edge) => {
        const relation = make("div", "implementation-subdomain-relation");
        append(
          relation,
          make("strong", "", `${edge.source.label} → ${edge.target.label}`),
          make("span", "", `${edge.edgeIds.length} 条静态 import`),
        );
        mapRelations.appendChild(relation);
      });
    }
    subdomainMap.appendChild(mapRelations);
    host.appendChild(subdomainMap);

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
      fact("分组依据", selectedArea.source === "target_profile" ? "目标配置规则" : "自动候选"),
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
    renderConceptualArchitecture();
    renderArchitectureGroups();
    renderArchitectureInspector();
    window.requestAnimationFrame(() => {
      drawConceptualLinks();
      drawArchitectureLinks();
    });
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
        make("div", "path-arrow", `→ ${window.PlainChangeI18n.translateText(path.relation_label)} →`),
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
      const originalClaim = sourceData.claims.find(item => item.id === claim.id);
      if (originalClaim && originalClaim.text !== claim.text) {
        const original = make("details", "claim-original");
        append(original, make("summary", "", "查看原始结论"), sourceText("p", "", originalClaim.text));
        body.appendChild(original);
      }
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
    byId("owner-map-back").addEventListener("click", () => {
      const focusId = state.ownerExpandedOverviewId || state.ownerOverviewSelectedId;
      state.ownerExpandedOverviewId = null;
      renderOwnerMap();
      document.querySelector(`[data-owner-node-id="${focusId}"]`)?.focus();
    });
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
        if (softwareControl && state.ownerExpandedOverviewId) {
          state.ownerExpandedOverviewId = null;
          renderOwnerMap();
          return;
        }
        if (state.architectureSelectedRelation) {
          state.architectureSelectedRelation = null;
          renderArchitecture();
        } else if (state.architectureSelectedNode) {
          state.architectureSelectedNode = null;
          renderArchitecture();
        } else if (state.architectureSelectedArea) {
          state.architectureSelectedArea = null;
          renderArchitecture();
        } else if (state.architectureSelectedGroup) {
          state.architectureSelectedGroup = null;
          state.architectureSelectedConcept = null;
          renderArchitecture();
        } else if (state.architectureSelectedConcept) {
          state.architectureSelectedConcept = null;
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
      resizeTimer = window.setTimeout(() => {
        drawConceptualLinks();
        drawArchitectureLinks();
        drawOwnerMapLinks();
      }, 100);
    });
  }

  renderHeader();
  renderSummary();
  renderGraph();
  renderBranches();
  renderInspector();
  bindEvents();
  enableSoftwareControlUI();
  if (!softwareControl && !architecture && !technicalPayload) {
    const architectureTab = document.querySelector('[data-page="architecture"]');
    architectureTab.disabled = true;
    architectureTab.title = "当前样本没有整体架构快照";
  }
  switchPage("change", false);
})();
