<script setup>
import * as echarts from "echarts";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";

import { API_STATISTICS } from "../api.js";

const loading = ref(true);
const error = ref(null);
const stats = ref(null);

const linesHistoryChartRef = ref(null);
let linesHistoryChartInstance = null;

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

const totalLines = computed(() => stats.value?.codebase?.total_lines);
const totalFiles = computed(() => stats.value?.codebase?.total_files);

/** Root weekly_lines_history; legacy: activity.derived.weekly_lines_history */
const weeklyLinesHistory = computed(() => {
  const root = stats.value;
  return (
    root?.weekly_lines_history ??
    root?.activity?.derived?.weekly_lines_history ??
    {}
  );
});

const weeklyLinesWeeks = computed(() => Object.keys(weeklyLinesHistory.value).sort());

function orderedExtensionsByTotal(history, weeks) {
  const extSet = new Set();
  for (const w of weeks) {
    const row = history[w];
    if (row && typeof row === "object") {
      Object.keys(row).forEach((e) => extSet.add(e));
    }
  }
  const exts = [...extSet];
  const totals = {};
  for (const e of exts) {
    let s = 0;
    for (const w of weeks) {
      const n = Number(history[w]?.[e]);
      s += Number.isFinite(n) ? n : 0;
    }
    totals[e] = s;
  }
  return exts.sort((a, b) => totals[b] - totals[a]);
}

const weeklyLinesExtensions = computed(() =>
  orderedExtensionsByTotal(weeklyLinesHistory.value, weeklyLinesWeeks.value),
);

function buildWeeklyLinesAreaOption() {
  const history = weeklyLinesHistory.value;
  const weeks = weeklyLinesWeeks.value;
  const exts = weeklyLinesExtensions.value;
  if (weeks.length === 0 || exts.length === 0) {
    return null;
  }

  const series = exts.map((ext) => ({
    name: ext,
    type: "line",
    stack: "total",
    areaStyle: {},
    emphasis: { focus: "series" },
    showSymbol: weeks.length <= 24,
    data: weeks.map((w) => {
      const n = Number(history[w]?.[ext]);
      return Number.isFinite(n) ? n : 0;
    }),
  }));

  return {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
    },
    legend: {
      data: exts,
      bottom: 0,
      type: "scroll",
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "18%",
      top: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: weeks,
      axisLabel: { rotate: weeks.length > 8 ? 35 : 0 },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
    },
    series,
  };
}

function syncLinesHistoryChart() {
  const weeks = weeklyLinesWeeks.value;
  if (weeks.length === 0 || weeklyLinesExtensions.value.length === 0) {
    linesHistoryChartInstance?.dispose();
    linesHistoryChartInstance = null;
    return;
  }
  if (!linesHistoryChartRef.value) {
    return;
  }
  const opt = buildWeeklyLinesAreaOption();
  if (!opt) {
    linesHistoryChartInstance?.clear();
    return;
  }
  if (!linesHistoryChartInstance) {
    linesHistoryChartInstance = echarts.init(linesHistoryChartRef.value);
  }
  linesHistoryChartInstance.setOption(opt, true);
}

function onResize() {
  linesHistoryChartInstance?.resize();
}

watch(
  [stats, weeklyLinesHistory, weeklyLinesWeeks, weeklyLinesExtensions],
  async () => {
    await nextTick();
    syncLinesHistoryChart();
  },
  { deep: true, flush: "post" },
);

onMounted(() => {
  load();
  window.addEventListener("resize", onResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", onResize);
  linesHistoryChartInstance?.dispose();
  linesHistoryChartInstance = null;
});
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold">Codebase</h1>

    <div v-if="loading" class="flex justify-center py-16">
      <span class="loading loading-lg loading-spinner text-primary" />
    </div>

    <div v-else-if="error" role="alert" class="alert alert-error">
      <span>{{ error }}</span>
    </div>

    <div v-else class="space-y-4">
      <p class="text-base-content/70 max-w-2xl text-sm">
        Repository composition, languages, and file metrics.
      </p>

      <div
        v-if="totalLines != null || totalFiles != null"
        class="text-sm text-base-content/80 flex flex-wrap gap-4"
      >
        <span v-if="totalFiles != null"
          ><span class="font-semibold text-base-content">Files:</span>
          {{ totalFiles.toLocaleString() }}</span
        >
        <span v-if="totalLines != null"
          ><span class="font-semibold text-base-content">Lines:</span>
          {{ totalLines.toLocaleString() }}</span
        >
      </div>

      <div class="card card-bordered bg-base-100 shadow-sm">
        <div class="border-b border-base-300 px-4 py-3 flex items-center gap-2">
          <span class="font-semibold">Lines of code by week</span>
          <div
            class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
            data-tip="Stacked area: estimated lines per file extension at the end of each week (weekly_lines_history)."
          >
            <button
              type="button"
              class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
              aria-label="About weekly lines history"
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
            v-if="weeklyLinesWeeks.length === 0 || weeklyLinesExtensions.length === 0"
            class="text-sm text-base-content/60 py-12 text-center"
          >
            No weekly lines history data.
          </div>
          <div v-else ref="linesHistoryChartRef" class="w-full min-h-[22rem]" />
        </div>
      </div>
    </div>
  </div>
</template>
