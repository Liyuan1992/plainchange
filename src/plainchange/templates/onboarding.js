(() => {
  const token = document.querySelector('meta[name="plainchange-session"]').content;
  const byId = (id) => document.getElementById(id);
  const pathInput = byId("repository-path");
  const inspectButton = byId("inspect-button");
  const pickButton = byId("pick-button");
  const projectMessage = byId("project-message");
  const versionsSection = byId("versions-section");
  const generateSection = byId("generate-section");
  const baseSelect = byId("base-select");
  const headSelect = byId("head-select");
  const taskInput = byId("task-input");
  const outputPath = byId("output-path");
  const analyzeButton = byId("analyze-button");
  const progressBox = byId("progress-box");
  const progressLabel = byId("progress-label");
  const progressPercent = byId("progress-percent");
  const progressBar = byId("progress-bar");
  const progressDetail = byId("progress-detail");
  const resultBox = byId("result-box");
  const openReport = byId("open-report");
  const errorMessage = byId("error-message");
  let repository = null;

  async function api(path, payload, method = "POST") {
    const response = await fetch(path, {
      method,
      headers: { "Content-Type": "application/json", "X-PlainChange-Token": token },
      body: method === "POST" ? JSON.stringify(payload || {}) : undefined,
    });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.error || "操作失败，请重试。");
    return data;
  }

  function setStep(number) {
    document.querySelectorAll(".step").forEach((item) => {
      item.classList.toggle("active", Number(item.dataset.step) <= number);
    });
  }

  function commitLabel(commit) {
    const date = new Date(commit.date);
    const readable = Number.isNaN(date.getTime()) ? commit.date : date.toLocaleDateString("zh-CN");
    return `${readable} · ${commit.message} · ${commit.short_id}`;
  }

  function fillSelect(select, commits, selected) {
    select.innerHTML = "";
    commits.forEach((commit) => {
      const option = document.createElement("option");
      option.value = commit.id;
      option.textContent = commitLabel(commit);
      option.selected = commit.id === selected;
      select.append(option);
    });
    select.disabled = false;
  }

  function refreshOutputPath() {
    if (!repository || !baseSelect.value || !headSelect.value) return;
    const separator = repository.output_root.includes("\\") ? "\\" : "/";
    outputPath.textContent = `${repository.output_root}${separator}${repository.output_stem}-${baseSelect.value.slice(0, 7).toLowerCase()}-to-${headSelect.value.slice(0, 7).toLowerCase()}`;
  }

  async function inspect() {
    projectMessage.textContent = "正在读取项目版本…";
    projectMessage.classList.remove("error");
    inspectButton.disabled = true;
    try {
      const data = await api("/api/repository", { path: pathInput.value });
      repository = data.repository;
      pathInput.value = repository.path;
      fillSelect(baseSelect, repository.commits, repository.default_base);
      fillSelect(headSelect, repository.commits, repository.default_head);
      outputPath.textContent = repository.default_output;
      byId("branch-chip").textContent = `${repository.name} · ${repository.branch}`;
      versionsSection.classList.remove("locked");
      generateSection.classList.remove("locked");
      analyzeButton.disabled = false;
      projectMessage.textContent = `已读取 ${repository.commits.length} 个最近版本，默认比较最近一次改动。`;
      setStep(2);
    } catch (error) {
      repository = null;
      projectMessage.textContent = error.message;
      projectMessage.classList.add("error");
    } finally {
      inspectButton.disabled = false;
    }
  }

  pickButton.addEventListener("click", async () => {
    pickButton.disabled = true;
    projectMessage.textContent = "正在打开文件夹选择器…";
    try {
      const data = await api("/api/pick-directory", {});
      if (data.path) {
        pathInput.value = data.path;
        await inspect();
      } else {
        projectMessage.textContent = "没有选择文件夹。";
      }
    } catch (error) {
      projectMessage.textContent = error.message;
      projectMessage.classList.add("error");
    } finally {
      pickButton.disabled = false;
    }
  });
  inspectButton.addEventListener("click", inspect);
  pathInput.addEventListener("keydown", (event) => { if (event.key === "Enter") inspect(); });
  baseSelect.addEventListener("change", refreshOutputPath);
  headSelect.addEventListener("change", refreshOutputPath);

  function updateProgress(job) {
    const receipt = job.receipt;
    const latest = receipt && receipt.latest_progress;
    const stages = receipt && Array.isArray(receipt.stages) ? receipt.stages : [];
    const finished = stages.filter((stage) => stage.status === "succeeded").length;
    const withinStage = latest && Number.isFinite(latest.percent) ? latest.percent / 100 : 0;
    let percent = Math.min(96, Math.round(((finished + withinStage) / 7) * 100));
    if (!receipt) percent = 4;
    if (job.status === "succeeded") percent = 100;
    progressPercent.textContent = `${percent}%`;
    progressBar.style.width = `${percent}%`;
    const active = stages.find((stage) => stage.status === "running");
    progressLabel.textContent = active ? active.label : job.status === "queued" ? "正在排队…" : "正在整理说明…";
    progressDetail.textContent = latest && latest.message ? latest.message : "只读取固定版本，不修改目标项目。";
  }

  async function poll(jobId) {
    try {
      const data = await api(`/api/jobs/${jobId}`, null, "GET");
      const job = data.job;
      updateProgress(job);
      if (job.status === "failed") throw new Error(job.error || "分析失败，请查看终端。 ");
      if (job.status === "succeeded") {
        progressBox.hidden = true;
        resultBox.hidden = false;
        openReport.href = `${job.report_url}?token=${encodeURIComponent(token)}`;
        analyzeButton.disabled = false;
        analyzeButton.textContent = "重新生成";
        setStep(3);
        return;
      }
      window.setTimeout(() => poll(jobId), 850);
    } catch (error) {
      progressBox.hidden = true;
      errorMessage.textContent = error.message;
      analyzeButton.disabled = false;
    }
  }

  analyzeButton.addEventListener("click", async () => {
    if (!repository) return;
    if (baseSelect.value === headSelect.value) {
      errorMessage.textContent = "较早版本和较新版本不能相同。";
      return;
    }
    analyzeButton.disabled = true;
    resultBox.hidden = true;
    errorMessage.textContent = "";
    progressBox.hidden = false;
    progressLabel.textContent = "正在固定两个版本…";
    progressPercent.textContent = "0%";
    progressBar.style.width = "0%";
    setStep(3);
    try {
      const data = await api("/api/analyze", {
        repository: repository.path,
        base: baseSelect.value,
        head: headSelect.value,
        task: taskInput.value,
        output: outputPath.textContent,
      });
      poll(data.job.id);
    } catch (error) {
      progressBox.hidden = true;
      errorMessage.textContent = error.message;
      analyzeButton.disabled = false;
    }
  });
})();
