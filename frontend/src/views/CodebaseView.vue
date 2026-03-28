<script setup>
import * as echarts from "echarts";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";

import { API_STATISTICS } from "../api.js";

const loading = ref(true);
const error = ref(null);
const stats = ref(null);

const linesChartRef = ref(null);
let linesChartInstance = null;

const filesChartRef = ref(null);
let filesChartInstance = null;

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

const codebase = computed(() => {
  const cb = stats.value?.codebase;
  return cb && typeof cb === "object" ? cb : null;
});

const linesByExtension = computed(() => codebase.value?.lines_by_extension ?? {});
const filesByExtension = computed(() => codebase.value?.files_by_extension ?? {});

/**
 * @param {Record<string, number>} raw
 * @param {{ valueLabel: string; seriesName: string }} labels
 */
function buildHorizontalBarOption(raw, { valueLabel, seriesName }) {
  const entries = Object.entries(raw).sort((a, b) => b[1] - a[1]);
  if (entries.length === 0) {
    return null;
  }

  const categories = entries.map(([ext]) => ext);
  const values = entries.map(([, n]) => n);

  const barCount = categories.length;
  const gridBottom = barCount > 12 ? "14%" : "8%";

  return {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (params) => {
        const p = Array.isArray(params) ? params[0] : params;
        if (!p) {
          return "";
        }
        return `${p.name}<br/>${p.value.toLocaleString()} ${valueLabel}`;
      },
    },
    grid: {
      left: "3%",
      right: "12%",
      top: "3%",
      bottom: gridBottom,
      containLabel: true,
    },
    xAxis: {
      type: "value",
      minInterval: 1,
    },
    yAxis: {
      type: "category",
      data: categories,
      inverse: true,
      axisLabel: {
        width: 120,
        overflow: "truncate",
      },
    },
    series: [
      {
        name: seriesName,
        type: "bar",
        data: values,
        emphasis: { focus: "series" },
        label: {
          show: barCount <= 24,
          position: "right",
          formatter: (p) => Number(p.value).toLocaleString(),
        },
      },
    ],
  };
}

function chartHeightPx(keyCount) {
  return Math.min(560, Math.max(280, keyCount * 28));
}

function syncLinesChart() {
  const raw = linesByExtension.value;
  if (Object.keys(raw).length === 0) {
    linesChartInstance?.dispose();
    linesChartInstance = null;
    return;
  }
  if (!linesChartRef.value) {
    return;
  }
  const opt = buildHorizontalBarOption(raw, {
    valueLabel: "lines",
    seriesName: "Lines",
  });
  if (!opt) {
    linesChartInstance?.clear();
    return;
  }
  if (!linesChartInstance) {
    linesChartInstance = echarts.init(linesChartRef.value);
  }
  linesChartInstance.setOption(opt, true);
}

function syncFilesChart() {
  const raw = filesByExtension.value;
  if (Object.keys(raw).length === 0) {
    filesChartInstance?.dispose();
    filesChartInstance = null;
    return;
  }
  if (!filesChartRef.value) {
    return;
  }
  const opt = buildHorizontalBarOption(raw, {
    valueLabel: "files",
    seriesName: "Files",
  });
  if (!opt) {
    filesChartInstance?.clear();
    return;
  }
  if (!filesChartInstance) {
    filesChartInstance = echarts.init(filesChartRef.value);
  }
  filesChartInstance.setOption(opt, true);
}

function syncCharts() {
  syncLinesChart();
  syncFilesChart();
}

function onResize() {
  linesChartInstance?.resize();
  filesChartInstance?.resize();
}

watch(
  [stats, linesByExtension, filesByExtension],
  async () => {
    await nextTick();
    syncCharts();
  },
  { deep: true, flush: "post" },
);

onMounted(() => {
  load();
  window.addEventListener("resize", onResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", onResize);
  linesChartInstance?.dispose();
  linesChartInstance = null;
  filesChartInstance?.dispose();
  filesChartInstance = null;
});

const totalLines = computed(() => stats.value?.codebase?.total_lines);
const totalFiles = computed(() => stats.value?.codebase?.total_files);
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
        Files and lines by extension (current tree scan).
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
          <span class="font-semibold">Lines by extension</span>
          <div
            class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
            data-tip="Number of text lines counted per file extension in the repository (excluding ignored paths and binary files)."
          >
            <button
              type="button"
              class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
              aria-label="About lines by extension"
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
            v-if="Object.keys(linesByExtension).length === 0"
            class="text-sm text-base-content/60 py-12 text-center"
          >
            No extension data in codebase report.
          </div>
          <div
            v-else
            ref="linesChartRef"
            class="w-full"
            :style="{ minHeight: `${chartHeightPx(Object.keys(linesByExtension).length)}px` }"
          />
        </div>
      </div>

      <div class="card card-bordered bg-base-100 shadow-sm">
        <div class="border-b border-base-300 px-4 py-3 flex items-center gap-2">
          <span class="font-semibold">Files by extension</span>
          <div
            class="tooltip tooltip-right before:max-w-xs before:text-left before:whitespace-normal"
            data-tip="Number of files per extension in the repository (excluding ignored paths and binary files)."
          >
            <button
              type="button"
              class="btn btn-ghost btn-xs btn-circle min-h-0 h-6 w-6 p-0"
              aria-label="About files by extension"
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
            v-if="Object.keys(filesByExtension).length === 0"
            class="text-sm text-base-content/60 py-12 text-center"
          >
            No file count data in codebase report.
          </div>
          <div
            v-else
            ref="filesChartRef"
            class="w-full"
            :style="{ minHeight: `${chartHeightPx(Object.keys(filesByExtension).length)}px` }"
          />
        </div>
      </div>
    </div>
  </div>
</template>
