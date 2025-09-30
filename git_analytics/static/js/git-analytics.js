const CHARTS = Object.create(null);

const authorColors = {};

function getAuthorColor(author) {
  if (!authorColors[author]) {
    const index = Object.keys(authorColors).length % BOOTSTRAP_COLORS.length;
    authorColors[author] = BOOTSTRAP_COLORS[index];
  }
  return authorColors[author];
}

const BOOTSTRAP_COLORS = [
  "#74c0fc",
  "#ced4da",
  "#8ce99a",
  "#ffa8a8",
  "#ffe066",
  "#66d9e8",
  "#b197fc",
  "#ffc078",
  "#63e6be",
  "#d0bfff",
  "#faa2c1",
  "#b2f2bb",
  "#f783ac",
  "#adb5bd",
  "#f1f3f5",
  "#868e96",
  "#e9ecef",
  "#495057",
  "#a5d8ff",
  "#ffd8a8" 
];

// main logic

document.addEventListener("DOMContentLoaded", () => {
  const menu = document.getElementById("rangeMenu");
  const btn = document.getElementById("rangeDropdownBtn");

  loadAndRender("months", 1, "Last month");

  menu.addEventListener("click", (e) => {
    const item = e.target.closest(".dropdown-item");
    if (!item) return;
    e.preventDefault();
    const type = item.dataset.type;
    const value = item.dataset.value;
    const label = item.textContent.trim();
    btn.textContent = item.textContent.trim();
    loadAndRender(type, value, label);
  });
});

async function loadAndRender(type, value, timeIntervalLabel) {
  try {
    // fetch stats
    const modalEl = document.getElementById("loadingModal");
    const modal = new bootstrap.Modal(modalEl, { backdrop: "static", keyboard: false });
    modal.show();  
    const stats = await fetchStatistics(type, value);
    modal.hide();

    // render stats
    renderGeneralStatistics(stats, timeIntervalLabel);
    renderWeeklyCommitTypes(stats.commit_type.commit_type_by_week);
    
    renderInsDelLinesByAuthors(stats.authors_statistics.authors);
    renderCodeChurnByAuthor(stats.authors_statistics.authors);
    renderCommitsByAuthor(stats.authors_statistics.authors);
    renderAccordionAuthors(stats);
    renderAuthorsContributionsTable(stats.authors_statistics.authors);
    
    buildHourByAuthorChart(stats.historical_statistics.hour_of_day);
    buildWeekByAuthorChart(stats.historical_statistics.day_of_week);
    buildDayOfMonthByAuthorChart(stats.historical_statistics.day_of_month);
    
    renderExtensionsHorizontalBar(stats.language_statistics.files_extensions_total);
    buildLinesOfCodeChart(stats.lines_statistics.items);
  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

async function fetchStatistics(type, value) {
  const range = computeRange(type, value);
  let url = "/api/statistics";
  if (range) {
    url += `?start_date=${range.start}&stop_date=${range.stop}`;
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch statistics");
  const data = await res.json();
  return data;
}

// helpers

function toISODate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function subMonths(date, n) {
  const d = new Date(date);
  const origDay = d.getDate();
  d.setDate(1);
  d.setMonth(d.getMonth() - n);
  const lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
  d.setDate(Math.min(origDay, lastDay));
  return d;
}

function computeRange(type, value) {
  if (type === "all") return null;

  const today = new Date();
  let start, stop;

  if (type === "days") {
    stop = today;
    start = new Date(today);
    start.setDate(start.getDate() - Number(value));
  } else if (type === "months") {
    stop = today;
    start = subMonths(today, Number(value));
  }

  return { start: toISODate(start), stop: toISODate(stop) };
}

// renderers

function renderGeneralStatistics(stats, rangeLabel) {
  const s = stats.commits_summary;
  if (!s) return;

  const summaryEl = document.getElementById("generalStatistics");
  if (!summaryEl) return;

  let branchInfo = "";
  if (stats.additional_data && stats.additional_data.name_branch) {
    branchInfo = `<strong>Branch:</strong> ${stats.additional_data.name_branch}<br>`;
  }

  summaryEl.innerHTML = `
      <div>
        <strong>Summary</strong> (${rangeLabel.toLowerCase()})<br>
        ${branchInfo}
        <strong>Contributors:</strong> ${s.total_number_authors}<br>
        <strong>Commits:</strong> ${s.total_number_commit}<br>
        <strong>First commit:</strong> ${s.date_first_commit}<br>
        <strong>Last commit:</strong> ${s.date_last_commit}
      </div>
  `;
}

function renderChart(id, config) {
  if (CHARTS[id]) {
    CHARTS[id].destroy();
  }
  const ctx = document.getElementById(id).getContext("2d");
  CHARTS[id] = new Chart(ctx, config);
}

function renderCommitsByAuthor(authorsData) {
  const chartName = "chartCommitsByAuthor";
  const labels = Object.keys(authorsData);
  const dataValues = Object.values(authorsData).map(a => a.commits);

  subRenderCommitsByAuthor(chartName, labels, dataValues);
}

function subRenderCommitsByAuthor(chartName, labels, values) {

  console.log("Rendering commits by author:", chartName, labels, values);

  renderChart(chartName, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [{
        data: values,
      }]
    },
    options: {
      backgroundColor: BOOTSTRAP_COLORS,
      responsive: true,
      plugins: { legend: { position: "bottom" } }
    }
  });
}

function renderCodeChurnByAuthor(authorsData) {
  const labels = Object.keys(authorsData);
  const dataValues = Object.values(authorsData).map(a => a.insertions + a.deletions);

  renderChart("chartCodeChurnByAuthor", {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: dataValues,
      }]
    },
    options: {
      backgroundColor: BOOTSTRAP_COLORS,
      responsive: true,
      plugins: { legend: { position: "bottom" } }
    }
  });
}


function renderInsDelLinesByAuthors(authorsData) {
  const labels = Object.keys(authorsData);

  const insertions = labels.map(a => authorsData[a].insertions || 0);
  const deletions  = labels.map(a => -(authorsData[a].deletions || 0));

  renderChart("chartInsDelLinesByAuthors", {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Insertions",
          data: insertions,
          borderWidth: 1,
          stack: "lines",
          backgroundColor: "#8ce99a"

        },
        {
          label: "Deletions",
          data: deletions,
          borderWidth: 1,
          stack: "lines",
          backgroundColor: "#f783ac"
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const v = ctx.parsed.y;
              return `${ctx.dataset.label}: ${v.toLocaleString()}`;
            }
          }
        }
      },
      scales: {
        x: { stacked: true },
        y: {
          stacked: true,
          beginAtZero: true,
          ticks: {
            callback: (v) => v.toLocaleString()
          }
        }
      }
    }
  });
}

function buildHourByAuthorChart(hourOfDayData) {
  const HOUR_LABELS = Array.from({ length: 24 }, (_, i) => String(i));

  const authors = new Set();
  for (const h of HOUR_LABELS) {
    Object.keys(hourOfDayData[h] || {}).forEach(a => authors.add(a));
  }

  if (authors.size === 0) {
    const totals = HOUR_LABELS.map(h => {
      const byAuthor = hourOfDayData[h] || {};
      return Object.values(byAuthor).reduce((s, v) => s + v, 0);
    });

    renderChart("chartDay", {
      type: "bar",
      data: { labels: HOUR_LABELS, datasets: [{
        label: "Total",
        data: totals,
        stack: "commits",
        borderWidth: 1
      }]},
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" },
          tooltip: { callbacks: { label: c => `${c.dataset.label}: ${c.parsed.y}` } }
        },
        scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
  }

  
  const datasets = Array.from(authors).map(author => ({
    label: author,
    data: HOUR_LABELS.map(h => {
      const v = hourOfDayData[h];
      return v && typeof v === "object" ? (v[author] ?? 0) : (v ?? 0);
    }),
    stack: "commits",
    borderWidth: 1,
    backgroundColor: getAuthorColor(author),
  }));

  renderChart("chartDay", {
    type: "bar",
    data: { labels: HOUR_LABELS, datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: { mode: "index", intersect: false,
          callbacks: { label: c => `${c.dataset.label}: ${c.parsed.y}` } }
      },
      scales: {
        x: { stacked: true},
        y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }
      }
    }
  });
}

function buildHourByAuthorChartForAccordion(chartName, dataValue) {
  const HOUR_LABELS = Array.from({ length: 24 }, (_, i) => String(i));

  renderChart(chartName, {
    type: "bar",
    data: {
      labels: HOUR_LABELS,
      datasets: [{
        data: dataValue,
        stack: "commits",
        borderWidth: 1,
        backgroundColor: "#74c0fc"
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom", display: false },
        tooltip: {
          callbacks: {
            label: (c) => `${c.dataset.label}: ${c.parsed.y}`
          }
        }
      },
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }
      }
    }
  });
}

function buildWeekByAuthorChart(dayOfWeekData) {
  const WEEK_LABELS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];

  const authors = new Set();
  for (const d of WEEK_LABELS) {
    Object.keys(dayOfWeekData[d] || {}).forEach(a => authors.add(a));
  }

  if (authors.size === 0) {
    const totals = WEEK_LABELS.map(d =>
      Object.values(dayOfWeekData[d] || {}).reduce((s, v) => s + v, 0)
    );

    renderChart("chartWeek", {
      type: "bar",
      data: {
        labels: WEEK_LABELS,
        datasets: [{
          label: "Total",
          data: totals,
          stack: "commits",
          borderWidth: 1,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" },
          tooltip: { callbacks: { label: c => `${c.dataset.label}: ${c.parsed.y}` } }
        },
        scales: {
          x: { stacked: true },
          y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });
    return;
  }

  const datasets = Array.from(authors).map(author => ({
    label: author,
    data: WEEK_LABELS.map(d => (dayOfWeekData[d] && dayOfWeekData[d][author]) || 0),
    stack: "commits",
    borderWidth: 1,
    backgroundColor: getAuthorColor(author),
  }));

  renderChart("chartWeek", {
    type: "bar",
    data: { labels: WEEK_LABELS, datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          mode: "index",
          intersect: false,
          callbacks: { label: c => `${c.dataset.label}: ${c.parsed.y}` }
        }
      },
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }
      }
    }
  });
}

function buildDayOfMonthByAuthorChart(dayOfMonthData) {
  const DAY_LABELS = Array.from({ length: 31 }, (_, i) => String(i + 1));

  const authors = new Set();
  for (const d of DAY_LABELS) {
    Object.keys(dayOfMonthData[d] || {}).forEach(a => authors.add(a));
  }

  if (authors.size === 0) {
    const totals = DAY_LABELS.map(d =>
      Object.values(dayOfMonthData[d] || {}).reduce((s, v) => s + v, 0)
    );

    renderChart("chartMonth", {
      type: "bar",
      data: {
        labels: DAY_LABELS,
        datasets: [{
          label: "Total",
          data: totals,
          stack: "commits",
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" },
          tooltip: { callbacks: { label: c => `${c.dataset.label}: ${c.parsed.y}` } }
        },
        scales: {
          x: { stacked: true, title: { display: true, text: "Day of Month" } },
          y: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: "Commits" } }
        }
      }
    });
    return;
  }

  const datasets = Array.from(authors).map(author => ({
    label: author,
    data: DAY_LABELS.map(d => (dayOfMonthData[d] && dayOfMonthData[d][author]) || 0),
    stack: "commits",
    borderWidth: 1,
    backgroundColor: getAuthorColor(author),
  }));

  renderChart("chartMonth", {
    type: "bar",
    data: { labels: DAY_LABELS, datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          mode: "index",
          intersect: false,
          callbacks: { label: c => `${c.dataset.label}: ${c.parsed.y}` }
        }
      },
      scales: {
        x: { stacked: true, title: { display: true, text: "Day of Month" } },
        y: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: "Commits" } }
      }
    }
  });
}

function renderExtensionsHorizontalBar(filesExtensionsTotal) {
  SubRenderExtensionsHorizontalBar("chartExtensions", filesExtensionsTotal)
}

function SubRenderExtensionsHorizontalBar(chartName, data) {
  const COLOR_INSERTIONS = "#198754";
  const COLOR_DELETIONS  = "#dc3545";

  const cleanKey = (k) => String(k).trim().replace(/}+$/, "");

  const items = Object.entries(data).map(([ext, v]) => {
    const key = cleanKey(ext) || "no_extension";
    const ins = Number(v?.insertions || 0);
    const del = Number(v?.deletions || 0);
    return { ext: key, insertions: ins, deletions: del };
  });

  const filtered = items.filter(it => it.insertions !== 0 || it.deletions !== 0);

  filtered.sort((a, b) => (b.insertions + b.deletions) - (a.insertions + a.deletions));

  const labels = filtered.map(it => it.ext);
  const insertions = filtered.map(it => it.insertions);
  const deletions  = filtered.map(it => -Math.abs(it.deletions)); // отрицательные

  renderChart(chartName, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Insertions",
          data: insertions,
          backgroundColor: COLOR_INSERTIONS,
          borderColor: COLOR_INSERTIONS,
          borderWidth: 1,
          stack: "lines"
        },
        {
          label: "Deletions",
          data: deletions,
          backgroundColor: COLOR_DELETIONS,
          borderColor: COLOR_DELETIONS,
          borderWidth: 1,
          stack: "lines"
        }
      ]
    },
    options: {
      responsive: true,
      indexAxis: "y",
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          mode: "index",
          intersect: false,
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            callback: (v) => Math.abs(v).toLocaleString()
          },
        },
        y: {
        }
      }
    }
  });
}

function buildLinesOfCodeChart(linesItems) {
  const sorted = [...linesItems].sort((a, b) => a.date.localeCompare(b.date));

  const labels = sorted.map(p => p.date);
  const values = sorted.map(p => p.lines);

  renderChart("chartLinesOfCode", {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Lines of Code",
        data: values,
        tension: 0.2,
        pointRadius: 2,
        borderWidth: 2,
        fill: false
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Lines: ${ctx.parsed.y.toLocaleString()}`
          }
        }
      },
      scales: {
        x: {
          
        },
        y: {
          beginAtZero: true,
          ticks: { callback: v => v.toLocaleString() }
        }
      }
    }
  });
}

function renderWeeklyCommitTypes(weeklyCommitTypesData) {
  const weeks = Object.keys(weeklyCommitTypesData).sort();

  const allCommitTypes = new Set();
  weeks.forEach(date => {
    Object.keys(weeklyCommitTypesData[date]).forEach(t => allCommitTypes.add(t));
  });

  const COMMIT_TYPE_COLORS = {
    feature: "#74c0fc",   // light blue
    fix: "#ffa8a8",       // soft red
    docs: "#ffd8a8",      // pastel peach
    style: "#d0bfff",     // soft purple
    refactor: "#ffc078",  // soft orange
    test: "#8ce99a",      // soft green
    chore: "#ced4da",     // light gray
    wip: "#faa2c1",       // soft pink
    merge: "#66d9e8",     // soft cyan
    unknown: "#adb5bd"    // neutral gray
  };

  const datasets = Array.from(allCommitTypes).map(type => ({
    label: type,
    data: weeks.map(week => weeklyCommitTypesData[week][type] ?? 0),
    stack: "commitTypes",
    borderWidth: 1,
    backgroundColor: COMMIT_TYPE_COLORS[type] || "#dee2e6" 
  }));

  renderChart("weeklyCommitTypes", {
    type: "bar",
    data: {
      labels: weeks,
      datasets: datasets
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          mode: "index",
          intersect: false,
        }
      },
      scales: {
        x: {
          stacked: true
        },
        y: {
          stacked: true,
          beginAtZero: true,
        }
      }
    }
  });
}

function renderAccordionAuthors(stats) {
  const authorsList = Object.keys(stats.authors_statistics.authors).sort();

  const accordion = document.getElementById("accordionAuthors");
  accordion.innerHTML = "";


  authorsList.forEach((author, index) => {
  const collapseId = `collapse-${index}`;
  const chartExtensionsId = `chartExtensions-${index}`;

  const chartCommitTypesId = `chartCommitTypes-${index}`;
  const chartCommitTypesLabels = Object.keys(stats.commit_type.author_commit_type_counter[author]);
  const chartCommitTypesValues = Object.values(stats.commit_type.author_commit_type_counter[author]);

  const chartDayId = `chartDay-${index}`;

  const chartDayValues = Object.keys(stats.historical_statistics.hour_of_day).map(h => stats.historical_statistics.hour_of_day[h][author] || 0);


  const item = document.createElement("div");
  item.className = "accordion-item";
  item.innerHTML = `
      <div class="accordion-item">
        <h2 class="accordion-header" id="heading-${index}">
          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
            ${author}
          </button>
        </h2>
        <div id="${collapseId}" class="accordion-collapse collapse" aria-labelledby="heading-${index}" data-bs-parent="#accordionAuthors">
          <div class="accordion-body">
            <div class="row">
              <div class="col-md-12">
                <canvas id="${chartExtensionsId}"></canvas>
              </div>
            </div>
            <div class="row">
              <div class="col-md-4">
                <canvas id="${chartCommitTypesId}"></canvas>
              </div>
              <div class="col-md-8">
                <canvas id="${chartDayId}"></canvas>
              </div>
            </div>
          </div>
        </div> 
    `;

    accordion.appendChild(item);

    setTimeout(() => {
      SubRenderExtensionsHorizontalBar(chartExtensionsId, stats.language_statistics.files_extensions_by_author[author]);
      subRenderCommitsByAuthor(chartCommitTypesId, chartCommitTypesLabels, chartCommitTypesValues);
      buildHourByAuthorChartForAccordion(chartDayId, chartDayValues);
    }, 0);
  });
}

function renderAuthorsContributionsTable(authorsData) {
  const tbody = document.getElementById("authorsContributionsTable");
  tbody.innerHTML = "";

  for (const [author, stats] of Object.entries(authorsData)) {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${author}</td>
      <td>${stats.commits}</td>
      <td>${stats.insertions.toLocaleString()}</td>
      <td>${stats.deletions.toLocaleString()}</td>
    `;

    tbody.appendChild(row);
  }
}