<script setup>
import * as echarts from "echarts";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";

import { API_STATISTICS } from "../api.js";

const COMMIT_TYPE_ORDER = [
  "feature",
  "fix",
  "docs",
  "style",
  "refactor",
  "test",
  "chore",
  "wip",
  "merge",
  "unknown",
];

const loading = ref(true);
const error = ref(null);
const stats = ref(null);

const chartRef = ref(null);
let chartInstance = null;

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

/** Root commits_summary; legacy: activity.commits_summary */
const commitsSummary = computed(() => {
  const root = stats.value;
  return root?.commits_summary ?? root?.activity?.commits_summary ?? {};
});

const commitTypeRaw = computed(() => {
  const root = stats.value;
  const ct = root?.commit_type ?? root?.activity?.commit_type;
  if (!ct || typeof ct !== "object") {
    return {};
  }
  if (ct.commit_type_by_week && typeof ct.commit_type_by_week === "object") {
    return ct.commit_type_by_week;
  }
  return ct;
});

const commitTypeWeeks = computed(() => {
  const raw = commitTypeRaw.value;
  return Object.keys(raw).sort();
});

const commitTypes = computed(() => {
  const raw = commitTypeRaw.value;
  const typeSet = new Set();
  for (const weekData of Object.values(raw)) {
    if (!weekData || typeof weekData !== "object") {
      continue;
    }
    Object.keys(weekData).forEach((t) => typeSet.add(t));
  }
  return orderedCommitTypes(typeSet);
});

const busFactorRaw = computed(() => {
  const root = stats.value;
  return (
    root?.bus_factor ??
    root?.risks?.bus_factor ??
    root?.post_data?.bus_factor ??
    root?.commits_summary?.post_data?.bus_factor
  );
});

const busFactor = computed(() => {
  const v = busFactorRaw.value;
  if (v == null) {
    return "—";
  }
  if (typeof v === "number") {
    return v;
  }
  if (typeof v === "object" && v.bus_factor != null) {
    return v.bus_factor;
  }
  return "—";
});

const busFactorAuthors = computed(() => {
  const v = busFactorRaw.value;
  if (typeof v === "object" && Array.isArray(v.authors)) {
    return v.authors;
  }
  return [];
});

const branch = computed(() => {
  const cs = commitsSummary.value;
  return (
    cs.branch_name ??
    stats.value?.additional_data?.name_branch ??
    "—"
  );
});

const contributorCount = computed(() => {
  const cs = commitsSummary.value;
  const n = cs.total_authors ?? cs.total_number_authors;
  return n == null ? undefined : n;
});

const codeChurn21dPercent = computed(() => {
  const root = stats.value;
  const ratio = codeChurn21dRaw.value?.churn_ratio;
  if (typeof ratio !== "number" || Number.isNaN(ratio)) {
    return "—";
  }
  return Math.round(ratio * 100);
});

const codeChurn21dRaw = computed(() => {
  const root = stats.value;
  return root?.code_churn_21d ?? root?.activity?.code_churn_21d ?? {};
});

const codeChurnAddedLines = computed(() => {
  const v = codeChurn21dRaw.value?.added_lines_in_period;
  return typeof v === "number" && !Number.isNaN(v) ? v : null;
});

const codeChurnDeletedLines = computed(() => {
  const v = codeChurn21dRaw.value?.short_lived_deleted_lines;
  return typeof v === "number" && !Number.isNaN(v) ? v : null;
});

function fmtScalar(v) {
  if (v == null || v === "") {
    return "null";
  }
  return String(v);
}

function orderedCommitTypes(typeSet) {
  const ordered = COMMIT_TYPE_ORDER.filter((t) => typeSet.has(t));
  const extra = [...typeSet].filter((t) => !COMMIT_TYPE_ORDER.includes(t)).sort();
  return [...ordered, ...extra];
}

function buildCommitTypesBarOption() {
  const raw = commitTypeRaw.value;
  const weeks = commitTypeWeeks.value;
  const types = commitTypes.value;
  if (weeks.length === 0 || types.length === 0) {
    return null;
  }
  const series = types.map((type) => ({
    name: type,
    type: "bar",
    stack: "total",
    emphasis: { focus: "series" },
    data: weeks.map((w) => {
      const count = raw[w]?.[type];
      const n = Number(count);
      return Number.isFinite(n) ? n : 0;
    }),
  }));

  return {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
    },
    legend: {
      data: types,
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

function syncWeeklyChart() {
  const weeks = commitTypeWeeks.value;
  if (weeks.length === 0) {
    chartInstance?.dispose();
    chartInstance = null;
    return;
  }
  if (!chartRef.value) {
    return;
  }
  const opt = buildCommitTypesBarOption();
  if (!opt) {
    chartInstance?.clear();
    return;
  }
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  chartInstance.setOption(opt, true);
}

function onResize() {
  chartInstance?.resize();
}

watch(
  [stats, commitTypeRaw, commitTypeWeeks, commitTypes],
  async () => {
    await nextTick();
    syncWeeklyChart();
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
});
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold">Overview</h1>

    <div v-if="loading" class="flex justify-center py-16">
      <span class="loading loading-lg loading-spinner text-primary" />
    </div>

    <div v-else-if="error" role="alert" class="alert alert-error">
      <span>{{ error }}</span>
    </div>

    <div
      v-else
      class="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch"
    >
      <!-- General statistics -->
      <div class="lg:col-span-4">
        <div class="card card-bordered bg-base-100 shadow-sm h-full">
          <div class="border-b border-base-300 px-4 py-3 flex items-center gap-2">
            <span class="font-semibold">General statistics</span>
            <div
              class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
              data-tip="Summary of repository activity for the selected time range."
            >
              <button
                type="button"
                class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
                aria-label="About general statistics"
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
          <div class="card-body p-4 pt-3">
            <p class="text-sm font-semibold text-base-content/80 mb-3">Summary (last month)</p>
            <dl class="space-y-2 text-sm">
              <div class="flex flex-wrap justify-between gap-x-4 gap-y-1">
                <dt class="font-bold">Branch</dt>
                <dd class="text-base-content/90">{{ branch }}</dd>
              </div>
              <div class="flex flex-wrap justify-between gap-x-4 gap-y-1">
                <dt class="font-bold">Contributors</dt>
                <dd class="text-base-content/90">
                  {{ fmtScalar(contributorCount) }}
                </dd>
              </div>
              <div class="flex flex-wrap justify-between gap-x-4 gap-y-1">
                <dt class="font-bold">Commits</dt>
                <dd class="text-base-content/90">
                  {{ fmtScalar(commitsSummary.total_number_commit) }}
                </dd>
              </div>
              <div class="flex flex-wrap justify-between gap-x-4 gap-y-1">
                <dt class="font-bold">First commit</dt>
                <dd class="text-base-content/90">
                  {{ fmtScalar(commitsSummary.date_first_commit) }}
                </dd>
              </div>
              <div class="flex flex-wrap justify-between gap-x-4 gap-y-1">
                <dt class="font-bold">Last commit</dt>
                <dd class="text-base-content/90">
                  {{ fmtScalar(commitsSummary.date_last_commit) }}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <!-- Bus factor -->
      <div class="lg:col-span-4">
        <div class="card card-bordered bg-base-100 shadow-sm h-full min-h-[12rem] flex flex-col">
          <div class="border-b border-base-300 px-4 py-3 flex items-center gap-2 shrink-0">
            <span class="font-semibold">Bus Factor</span>
            <div
              class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
              data-tip="The bus factor is the minimum number of developers that would have to leave before the project loses critical knowledge. Lower values mean higher concentration of knowledge."
            >
              <button
                type="button"
                class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
                aria-label="About bus factor"
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
          <div class="card-body grow p-6">
            <div class="h-full grid grid-cols-2 gap-4 items-center">
              <div class="flex items-center justify-center border-r border-base-300 pr-4">
                <p class="text-6xl font-bold text-error tabular-nums leading-none">
                  {{ busFactor }}
                </p>
              </div>
              <div class="min-w-0">
                <p class="text-xs uppercase tracking-wide text-base-content/60 mb-2">Authors</p>
                <ul
                  v-if="busFactorAuthors.length > 0"
                  class="text-sm font-medium space-y-1 max-h-40 overflow-auto"
                >
                  <li v-for="author in busFactorAuthors" :key="author" class="truncate">
                    {{ author }}
                  </li>
                </ul>
                <p v-else class="text-sm text-base-content/60">No authors data</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Code churn 21d -->
      <div class="lg:col-span-4">
        <div class="card card-bordered bg-base-100 shadow-sm h-full min-h-[12rem] flex flex-col">
          <div class="border-b border-base-300 px-4 py-3 flex items-center gap-2 shrink-0">
            <span class="font-semibold">Code Churn 21d</span>
            <div
              class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
              data-tip="Short-lived deleted lines over added lines in the reporting period. Value is churn_ratio * 100, rounded."
            >
              <button
                type="button"
                class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
                aria-label="About code churn 21d"
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
          <div class="card-body grow p-6">
            <div class="h-full grid grid-cols-2 gap-4 items-center">
              <div class="text-sm text-base-content/80 leading-relaxed pr-2">
                Over the last 21 days, {{ fmtScalar(codeChurnAddedLines) }} lines were added, of which
                {{ fmtScalar(codeChurnDeletedLines) }} were deleted.
              </div>
              <div class="flex items-center justify-center border-l border-base-300 pl-4">
                <p class="text-6xl font-bold text-warning tabular-nums leading-none">
                  {{ codeChurn21dPercent }}
                  <span class="text-2xl align-top">%</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Weekly commit types -->
      <div class="lg:col-span-12">
        <div class="card card-bordered bg-base-100 shadow-sm">
          <div class="border-b border-base-300 px-4 py-3 flex items-center gap-2">
            <span class="font-semibold">Weekly commit types</span>
            <div
              class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
              data-tip="Stacked bar chart by week (e.g. 21W47, 21W48), where each color is a commit type and value is commits in that week."
            >
              <button
                type="button"
                class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
                aria-label="About weekly commit types"
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
              v-if="commitTypeWeeks.length === 0"
              class="text-sm text-base-content/60 py-12 text-center"
            >
              No commit type data for the selected range.
            </div>
            <div v-else ref="chartRef" class="w-full min-h-[22rem]" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
