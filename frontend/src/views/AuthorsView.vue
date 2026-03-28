<script setup>
import * as echarts from "echarts";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";

import { API_STATISTICS } from "../api.js";

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

/** Root authors_statistics or author -> stats; legacy: activity / nested .authors */
const authorsStats = computed(() => {
  const root = stats.value;
  const pick =
    root?.authors_statistics ??
    root?.activity?.authors_statistics;
  if (pick == null) {
    return {};
  }
  if (pick.authors != null && typeof pick.authors === "object") {
    return pick.authors;
  }
  return pick;
});

/** Pie slices: commit count per author (desc). */
const commitsByAuthor = computed(() => {
  const raw = authorsStats.value;
  if (!raw || typeof raw !== "object") {
    return [];
  }
  return Object.entries(raw)
    .map(([name, v]) => ({
      name,
      value: v?.commits ?? 0,
    }))
    .filter((x) => x.value > 0)
    .sort((a, b) => b.value - a.value);
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
    },
    series: [
      {
        name: "Commits",
        type: "pie",
        radius: ["38%", "68%"],
        center: ["50%", "46%"],
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

function onResize() {
  chartInstance?.resize();
}

watch(
  [stats, commitsByAuthor],
  async () => {
    await nextTick();
    syncChart();
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

      <div class="card card-bordered bg-base-100 shadow-sm">
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
          <div v-else ref="chartRef" class="w-full min-h-[24rem]" />
        </div>
      </div>
    </div>
  </div>
</template>
