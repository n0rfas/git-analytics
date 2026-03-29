<script setup>
import * as echarts from "echarts";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";

import { API_STATISTICS } from "../api.js";

const loading = ref(true);
const error = ref(null);
const stats = ref(null);

const chartRef = ref(null);
let chartInstance = null;

const churnChartRef = ref(null);
let churnChartInstance = null;

const insDelChartRef = ref(null);
let insDelChartInstance = null;

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const r = await fetch(API_STATISTICS);
    if (!r.ok) {
      throw new Error(r.statusText || String(r.status));
    }
    stats.value = await r.json();
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Failed to load statistics";
  } finally {
    loading.value = false;
  }
}

function unwrapAuthorMap(pick) {
  if (pick == null || typeof pick !== "object") {
    return {};
  }
  if (pick.authors != null && typeof pick.authors === "object") {
    return pick.authors;
  }
  return pick;
}

/** Root author_statistics (preferred), authors_statistics; legacy: activity */
const authorsStats = computed(() => {
  const root = stats.value;
  const pick =
    root?.author_statistics ??
    root?.authors_statistics ??
    root?.activity?.authors_statistics;
  return unwrapAuthorMap(pick);
});

/** Pie slices: commit count per author (desc). Counts from root `commits` map if present, else author -> .commits */
const commitsByAuthor = computed(() => {
  const root = stats.value;

  const direct = root?.commits;
  if (direct && typeof direct === "object" && !Array.isArray(direct)) {
    const vals = Object.values(direct);
    if (
      vals.length > 0 &&
      vals.every((v) => typeof v === "number" || (typeof v === "string" && v !== "" && !Number.isNaN(Number(v))))
    ) {
      return Object.entries(direct)
        .map(([name, value]) => ({ name, value: Number(value) || 0 }))
        .filter((x) => x.value > 0)
        .sort((a, b) => b.value - a.value);
    }
  }

  const nestedCommits =
    root?.author_statistics?.commits ?? root?.authors_statistics?.commits;
  if (nestedCommits && typeof nestedCommits === "object" && !Array.isArray(nestedCommits)) {
    const vals = Object.values(nestedCommits);
    if (
      vals.length > 0 &&
      vals.every((v) => typeof v === "number" || (typeof v === "string" && v !== "" && !Number.isNaN(Number(v))))
    ) {
      return Object.entries(nestedCommits)
        .map(([name, value]) => ({ name, value: Number(value) || 0 }))
        .filter((x) => x.value > 0)
        .sort((a, b) => b.value - a.value);
    }
  }

  const raw = authorsStats.value;
  if (!raw || typeof raw !== "object") {
    return [];
  }
  return Object.entries(raw)
    .map(([name, v]) => ({
      name,
      value: typeof v === "number" ? v : (v?.commits ?? 0),
    }))
    .filter((x) => x.value > 0)
    .sort((a, b) => b.value - a.value);
});

/** Per-author code churn (insertions + deletions) from author_statistics[].code_churn */
const codeChurnByAuthor = computed(() => {
  const raw = authorsStats.value;
  if (!raw || typeof raw !== "object") {
    return [];
  }
  return Object.entries(raw)
    .map(([name, v]) => {
      let churn = 0;
      if (v && typeof v === "object") {
        const c = Number(v.code_churn);
        churn = Number.isFinite(c) ? c : 0;
      }
      return { name, value: churn };
    })
    .filter((x) => x.value > 0)
    .sort((a, b) => b.value - a.value);
});

/** Insertions / deletions per author (author_statistics.insertions, .deletions) */
const insertionsDeletionsByAuthor = computed(() => {
  const raw = authorsStats.value;
  if (!raw || typeof raw !== "object") {
    return [];
  }
  return Object.entries(raw)
    .map(([name, v]) => {
      if (!v || typeof v !== "object") {
        return { name, insertions: 0, deletions: 0 };
      }
      const ins = Number(v.insertions);
      const del = Number(v.deletions);
      return {
        name,
        insertions: Number.isFinite(ins) ? ins : 0,
        deletions: Number.isFinite(del) ? del : 0,
      };
    })
    .filter((x) => x.insertions > 0 || x.deletions > 0)
    .sort((a, b) => a.name.localeCompare(b.name));
});

function buildPieOption() {
  const data = commitsByAuthor.value;
  if (data.length === 0) {
    return null;
  }
  return {
    tooltip: {
      trigger: "item",
      formatter: "{b}<br/>{c} commits ({d}%)",
    },
    legend: {
      type: "scroll",
      bottom: 0,
      left: "center",
      itemWidth: 10,
      itemHeight: 8,
      textStyle: { fontSize: 11 },
    },
    series: [
      {
        name: "Commits",
        type: "pie",
        radius: ["32%", "58%"],
        center: ["50%", "42%"],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
        },
        label: {
          show: true,
          formatter: "{b}\n{d}%",
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 12,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.25)",
          },
        },
        data,
      },
    ],
  };
}

function syncChart() {
  const data = commitsByAuthor.value;
  if (data.length === 0) {
    chartInstance?.dispose();
    chartInstance = null;
    return;
  }
  if (!chartRef.value) {
    return;
  }
  const opt = buildPieOption();
  if (!opt) {
    chartInstance?.clear();
    return;
  }
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  chartInstance.setOption(opt, true);
}

function buildChurnPieOption() {
  const data = codeChurnByAuthor.value;
  if (data.length === 0) {
    return null;
  }
  return {
    tooltip: {
      trigger: "item",
      formatter: "{b}<br/>{c} lines churn ({d}%)",
    },
    legend: {
      type: "scroll",
      bottom: 0,
      left: "center",
      itemWidth: 10,
      itemHeight: 8,
      textStyle: { fontSize: 11 },
    },
    series: [
      {
        name: "Code churn",
        type: "pie",
        radius: ["32%", "58%"],
        center: ["50%", "42%"],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
        },
        label: {
          show: true,
          formatter: "{b}\n{d}%",
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 12,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.25)",
          },
        },
        data,
      },
    ],
  };
}

function syncChurnChart() {
  const rows = codeChurnByAuthor.value;
  if (rows.length === 0) {
    churnChartInstance?.dispose();
    churnChartInstance = null;
    return;
  }
  if (!churnChartRef.value) {
    return;
  }
  const opt = buildChurnPieOption();
  if (!opt) {
    churnChartInstance?.clear();
    return;
  }
  if (!churnChartInstance) {
    churnChartInstance = echarts.init(churnChartRef.value);
  }
  churnChartInstance.setOption(opt, true);
}

function buildInsDelBarOption() {
  const rows = insertionsDeletionsByAuthor.value;
  if (rows.length === 0) {
    return null;
  }
  const authors = rows.map((r) => r.name);
  const insData = rows.map((r) => r.insertions);
  const delData = rows.map((r) => -r.deletions);

  return {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter(params) {
        const list = Array.isArray(params) ? params : [params];
        const first = list[0];
        const author = first?.axisValue ?? first?.name ?? "";
        let html = String(author);
        for (const p of list) {
          const rawVal = Number(p.value);
          const abs = Math.abs(rawVal);
          const label = p.seriesName === "Deletions" ? "Deletions" : "Insertions";
          html += `<br/>${label}: ${abs.toLocaleString()} lines`;
        }
        return html;
      },
    },
    legend: {
      data: ["Insertions", "Deletions"],
      bottom: 0,
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "14%",
      top: "8%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: authors,
      axisLabel: { rotate: authors.length > 12 ? 35 : 0 },
    },
    yAxis: {
      type: "value",
      axisLabel: {
        formatter: (val) => Math.abs(val).toLocaleString(),
      },
      splitLine: {
        show: true,
        lineStyle: { type: "dashed", opacity: 0.35 },
      },
    },
    series: [
      {
        name: "Insertions",
        type: "bar",
        data: insData,
        itemStyle: { color: "#22c55e" },
      },
      {
        name: "Deletions",
        type: "bar",
        data: delData,
        itemStyle: { color: "#ef4444" },
      },
    ],
  };
}

function syncInsDelChart() {
  const rows = insertionsDeletionsByAuthor.value;
  if (rows.length === 0) {
    insDelChartInstance?.dispose();
    insDelChartInstance = null;
    return;
  }
  if (!insDelChartRef.value) {
    return;
  }
  const opt = buildInsDelBarOption();
  if (!opt) {
    insDelChartInstance?.clear();
    return;
  }
  if (!insDelChartInstance) {
    insDelChartInstance = echarts.init(insDelChartRef.value);
  }
  insDelChartInstance.setOption(opt, true);
}

function onResize() {
  chartInstance?.resize();
  churnChartInstance?.resize();
  insDelChartInstance?.resize();
}

watch(
  [stats, commitsByAuthor, codeChurnByAuthor, insertionsDeletionsByAuthor],
  async () => {
    await nextTick();
    syncChart();
    syncChurnChart();
    syncInsDelChart();
  },
  { deep: true, flush: "post" },
);

onMounted(() => {
  load();
  window.addEventListener("resize", onResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", onResize);
  chartInstance?.dispose();
  chartInstance = null;
  churnChartInstance?.dispose();
  churnChartInstance = null;
  insDelChartInstance?.dispose();
  insDelChartInstance = null;
});
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold">Authors</h1>

    <div v-if="loading" class="flex justify-center py-16">
      <span class="loading loading-lg loading-spinner text-primary" />
    </div>

    <div v-else-if="error" role="alert" class="alert alert-error">
      <span>{{ error }}</span>
    </div>

    <div v-else class="space-y-4">
      <p class="text-base-content/70 max-w-2xl text-sm">
        Contributions, churn, and activity by author.
      </p>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 items-stretch">
        <div class="min-w-0">
          <div class="card card-bordered bg-base-100 shadow-sm h-full">
            <div class="border-b border-base-300 px-4 py-3 flex items-center gap-2">
              <span class="font-semibold">Commits by author</span>
              <div
                class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
                data-tip="Share of total commits in the selected time range, per author."
              >
                <button
                  type="button"
                  class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
                  aria-label="About commits by author chart"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4 opacity-60"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </button>
              </div>
            </div>
            <div class="card-body p-4">
              <div
                v-if="commitsByAuthor.length === 0"
                class="text-sm text-base-content/60 py-12 text-center"
              >
                No commit data by author for the selected range.
              </div>
              <div v-else ref="chartRef" class="w-full min-h-[12rem]" />
            </div>
          </div>
        </div>

        <div class="min-w-0">
          <div class="card card-bordered bg-base-100 shadow-sm h-full">
            <div class="border-b border-base-300 px-4 py-3 flex items-center gap-2">
              <span class="font-semibold">Code churn by author</span>
              <div
                class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
                data-tip="Sum of insertions and deletions per author (author_statistics.code_churn)."
              >
                <button
                  type="button"
                  class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
                  aria-label="About code churn by author"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4 opacity-60"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </button>
              </div>
            </div>
            <div class="card-body p-4">
              <div
                v-if="codeChurnByAuthor.length === 0"
                class="text-sm text-base-content/60 py-12 text-center"
              >
                No code churn data by author.
              </div>
              <div v-else ref="churnChartRef" class="w-full min-h-[12rem]" />
            </div>
          </div>
        </div>
      </div>

      <div class="card card-bordered bg-base-100 shadow-sm w-full">
        <div class="border-b border-base-300 px-4 py-3 flex items-center gap-2">
          <span class="font-semibold">Insertions &amp; deletions by author</span>
          <div
            class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
            data-tip="Green bars above the axis: lines added. Red bars below: lines removed (author_statistics.insertions / deletions)."
          >
            <button
              type="button"
              class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
              aria-label="About insertions and deletions chart"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 opacity-60"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body p-4">
          <div
            v-if="insertionsDeletionsByAuthor.length === 0"
            class="text-sm text-base-content/60 py-12 text-center"
          >
            No insertions or deletions data by author.
          </div>
          <div v-else ref="insDelChartRef" class="w-full min-h-[28rem]" />
        </div>
      </div>
    </div>
  </div>
</template>
