<script setup>
import * as echarts from "echarts";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";

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
    const r = await fetch("/api/statistics");
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

const commitsSummary = computed(() => stats.value?.commits_summary ?? {});

const commitTypeByWeek = computed(
  () => stats.value?.commit_type?.commit_type_by_week ?? {},
);

const busFactor = computed(() => {
  const root = stats.value?.post_data?.bus_factor;
  const nested = stats.value?.commits_summary?.post_data?.bus_factor;
  const v = root ?? nested;
  return v == null ? "—" : v;
});

const branch = computed(() => stats.value?.additional_data?.name_branch ?? "—");

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

function buildWeeklyCommitTypesOption() {
  const raw = commitTypeByWeek.value;
  const weeks = Object.keys(raw).sort();
  if (weeks.length === 0) {
    return null;
  }

  const typeSet = new Set();
  for (const w of weeks) {
    Object.keys(raw[w] || {}).forEach((t) => typeSet.add(t));
  }
  const types = orderedCommitTypes(typeSet);

  const series = types.map((type) => ({
    name: type,
    type: "bar",
    stack: "total",
    emphasis: { focus: "series" },
    data: weeks.map((w) => raw[w]?.[type] ?? 0),
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
  const raw = commitTypeByWeek.value;
  if (Object.keys(raw).length === 0) {
    chartInstance?.dispose();
    chartInstance = null;
    return;
  }
  if (!chartRef.value) {
    return;
  }
  const opt = buildWeeklyCommitTypesOption();
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
  [stats, commitTypeByWeek],
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
      <div class="lg:col-span-8">
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
                  {{ fmtScalar(commitsSummary.total_number_authors) }}
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
          <div class="card-body grow flex items-center justify-center p-6">
            <p class="text-7xl font-bold text-error tabular-nums leading-none">
              {{ busFactor }}
            </p>
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
              data-tip="Commits per ISO week, stacked by inferred type from commit messages (feature, fix, docs, …). One commit can count in multiple types."
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
              v-if="Object.keys(commitTypeByWeek).length === 0"
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
