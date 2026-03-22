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
    path: "/commits",
    name: "commits",
    component: () => import("../views/CommitsView.vue"),
  },
];

export default createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes,
});
