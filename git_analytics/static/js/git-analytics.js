const CHARTS = Object.create(null);

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

async function loadAndRender(type, value, label) {
  try {
    // fetch stats
    const modalEl = document.getElementById("loadingModal");
    const modal = new bootstrap.Modal(modalEl, { backdrop: "static", keyboard: false });
    modal.show();  
    const stats = await fetchStatistics(type, value);
    modal.hide();

    // render stats
    renderSummary(stats, label);
    buildAuthorsChart(stats.authors_statistics.authors);
    buildAuthorsStackedChart(stats.authors_statistics.authors);
    buildHourByAuthorChart(stats.historical_statistics.hour_of_day);
    buildWeekByAuthorChart(stats.historical_statistics.day_of_week);
    buildDayOfMonthByAuthorChart(stats.historical_statistics.day_of_month);
    buildLinesChart(stats.lines_statistics.items);
    buildCommitTypeChart(stats.commit_type.items);
    buildAuthorsTable(stats.authors_statistics.authors);

  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

function renderSummary(stats, rangeLabel) {
  const s = stats.commits_summary;
  if (!s) return;

  const summaryEl = document.getElementById("titleBranch");
  if (!summaryEl) return;

  summaryEl.innerHTML = `
      <div>
        <strong>Statistics for:</strong> ${rangeLabel.toLowerCase()}<br>
        <strong>Total number of authors:</strong> ${s.total_number_authors}<br>
        <strong>Total number of commits:</strong> ${s.total_number_commit}<br>
        <strong>Date of the first commit:</strong> ${s.date_first_commit}<br>
        <strong>Date of the last commit:</strong> ${s.date_last_commit}
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

function buildAuthorsChart(authorsData) {
  const labels = Object.keys(authorsData);
  const dataValues = Object.values(authorsData).map(a => a.commits);

  const ctx = document.getElementById("chartAuthors").getContext("2d");

  renderChart("chartAuthors", {
    type: "pie",
    data: {
      labels: labels,
      datasets: [{
        data: dataValues,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom" } }
    }
  });
}

function buildAuthorsStackedChart(authorsData) {
  const labels = Object.keys(authorsData);

  const insertions = labels.map(a => authorsData[a].insertions || 0);
  const deletions  = labels.map(a => -(authorsData[a].deletions || 0));

  const ctx = document.getElementById("chartAuthors2").getContext("2d");

  renderChart("chartAuthors2", {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Insertions",
          data: insertions,
          borderWidth: 1,
          stack: "lines"
        },
        {
          label: "Deletions",
          data: deletions,
          borderWidth: 1,
          stack: "lines"
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
  
  const HOUR_LABELS = Array.from({ length: 24 }, (_, i) => i.toString());

  const authors = new Set();
  for (const h of Object.keys(hourOfDayData)) {
    const v = hourOfDayData[h];
    if (v && typeof v === "object") {
      Object.keys(v).forEach(a => authors.add(a));
    }
  }

  const ctx = document.getElementById("chartDay").getContext("2d");

  
  if (authors.size === 0) {
    const totals = HOUR_LABELS.map(h => hourOfDayData[h] ?? 0);

    renderChart("chartDay", {
      type: "bar",
      data: { labels: HOUR_LABELS, datasets: [{ label: "Total", data: totals, stack: "commits", borderWidth: 1 }] },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" },
          tooltip: { callbacks: { label: c => `${c.dataset.label}: ${c.parsed.y}` } }
        },
        scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
    return;
  }

  
  const datasets = Array.from(authors).map(author => ({
    label: author,
    data: HOUR_LABELS.map(h => {
      const v = hourOfDayData[h];
      return v && typeof v === "object" ? (v[author] ?? 0) : (v ?? 0);
    }),
    stack: "commits",
    borderWidth: 1
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

function buildWeekByAuthorChart(dayOfWeekData) {
  const WEEK_LABELS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];

  const authors = new Set();
  for (const day of Object.keys(dayOfWeekData)) {
    const v = dayOfWeekData[day];
    if (v && typeof v === "object") {
      Object.keys(v).forEach(a => authors.add(a));
    }
  }

  const ctx = document.getElementById("chartWeek").getContext("2d");

  if (authors.size === 0) {
    const totals = WEEK_LABELS.map(d => dayOfWeekData[d] ?? 0);
    renderChart("chartWeek", {
      type: "bar",
      data: {
        labels: WEEK_LABELS,
        datasets: [{ label: "Total", data: totals, borderWidth: 1, stack: "commits" }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" },
          tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${c.parsed.y}` } }
        },
        scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
    return;
  }

  const datasets = Array.from(authors).map((author, idx) => ({
    label: author,
    data: WEEK_LABELS.map(day => {
      const v = dayOfWeekData[day];
      return v && typeof v === "object" ? (v[author] ?? 0) : 0;
    }),
    borderWidth: 1,
    stack: "commits"
  }));

  renderChart("chartWeek", {
    type: "bar",
    data: { labels: WEEK_LABELS, datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: { mode: "index", intersect: false,
          callbacks: { label: (c) => `${c.dataset.label}: ${c.parsed.y}` } }
      },
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }
      }
    }
  });
}

function buildDayOfMonthByAuthorChart(dayOfMonthData) {
  const DAY_LABELS = Array.from({ length: 31 }, (_, i) => (i + 1).toString());

  const authors = new Set();
  for (const d of Object.keys(dayOfMonthData)) {
    const v = dayOfMonthData[d];
    if (v && typeof v === "object") {
      Object.keys(v).forEach(a => authors.add(a));
    }
  }

  const ctx = document.getElementById("chartMonth").getContext("2d");

  if (authors.size === 0) {
    const totals = DAY_LABELS.map(d => dayOfMonthData[d] ?? 0);
    renderChart("chartMonth", {
      type: "bar",
      data: { labels: DAY_LABELS, datasets: [{ label: "Total", data: totals, stack: "commits", borderWidth: 1 }] },
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
    data: DAY_LABELS.map(d => {
      const v = dayOfMonthData[d];
      return v && typeof v === "object" ? (v[author] ?? 0) : (v ?? 0);
    }),
    stack: "commits",
    borderWidth: 1
  }));

  renderChart("chartMonth", {
    type: "bar",
    data: { labels: DAY_LABELS, datasets },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          mode: "index", intersect: false,
          callbacks: { label: c => `${c.dataset.label}: ${c.parsed.y}` }
        }
      },
      scales: {
        x: { stacked: true},
        y: { stacked: true, beginAtZero: true, ticks: { precision: 0 }}
      }
    }
  });
}

function buildLinesChart(linesItems) {
  const sorted = [...linesItems].sort((a, b) => a.date.localeCompare(b.date));

  const labels = sorted.map(p => p.date);
  const values = sorted.map(p => p.lines);

  const ctx = document.getElementById("chartLines").getContext("2d");

  renderChart("chartLines", {
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

function buildCommitTypeChart(commitTypeData) {
  const ctx = document.getElementById("typesCommits").getContext("2d");
  const dates = Object.keys(commitTypeData).sort();

  
  const commitTypes = new Set();
  dates.forEach(date => {
    Object.keys(commitTypeData[date]).forEach(type => commitTypes.add(type));
  });

  
  const datasets = Array.from(commitTypes).map((type, i) => ({
    label: type,
    data: dates.map(date => commitTypeData[date][type] || 0),
    stack: "commitTypes"
  }));

  renderChart("typesCommits", {
    type: "bar",
    data: {
      labels: dates,
      datasets: datasets
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          mode: "index",
          intersect: false
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

function buildAuthorsTable(authorsData) {
  const tbody = document.getElementById("authorsTableBody");
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

// start
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