import { createRouter, createWebHashHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "overview",
    component: () => import("../views/OverviewView.vue"),
  },
  {
    path: "/authors",
    name: "authors",
    component: () => import("../views/AuthorsView.vue"),
  },
  {
    path: "/codebase",
    name: "codebase",
    component: () => import("../views/CodebaseView.vue"),
  },
];

export default createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes,
});
