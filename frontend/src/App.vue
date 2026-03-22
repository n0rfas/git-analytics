<script setup>
import { onMounted, ref, watch } from "vue";

const STORAGE_KEY = "git-analytics-daisyui-theme";

const themes = [
  "light",
  "dark",
  "cupcake",
  "corporate",
  "synthwave",
  "night",
  "nord",
  "sunset",
];

const theme = ref("light");

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved && themes.includes(saved)) {
    theme.value = saved;
  }
  document.documentElement.setAttribute("data-theme", theme.value);
});

watch(theme, (value) => {
  document.documentElement.setAttribute("data-theme", value);
  localStorage.setItem(STORAGE_KEY, value);
});

const nav = [
  { to: "/", label: "Overview" },
  { to: "/authors", label: "Authors" },
  { to: "/commits", label: "Commits" },
];
</script>

<template>
  <div class="min-h-screen bg-base-200 text-base-content flex flex-col">
    <header class="navbar bg-base-100 shadow-sm border-b border-base-300 px-4 shrink-0">
      <div class="flex-1">
        <RouterLink to="/" class="text-lg font-semibold tracking-tight link link-hover">
          Git-Analytics
        </RouterLink>
      </div>
      <div class="flex-none gap-2">
        <label class="form-control">
          <span class="label-text sr-only">Theme</span>
          <select v-model="theme" class="select select-bordered select-sm max-w-xs">
            <option v-for="t in themes" :key="t" :value="t">
              {{ t }}
            </option>
          </select>
        </label>
      </div>
    </header>

    <div class="flex flex-1 min-h-0">
      <aside
        class="w-56 shrink-0 border-r border-base-300 bg-base-100 flex flex-col p-3"
        aria-label="Main navigation"
      >
        <ul class="menu rounded-box w-full p-0 gap-0.5">
          <li v-for="item in nav" :key="item.to">
            <RouterLink :to="item.to" active-class="active" class="font-medium">
              {{ item.label }}
            </RouterLink>
          </li>
        </ul>
      </aside>

      <main class="flex-1 overflow-auto p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
