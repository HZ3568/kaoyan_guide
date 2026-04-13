import request from "@/utils/request.js";

// ==================== 咨询会话管理 ====================

export const sessionList = (params) => {
  return request.get("/admin/ai/session/list", { params });
};

export const sessionHistory = (memoryKey) => {
  return request.get("/admin/ai/session/history", { params: { memoryKey } });
};

export const sessionDelete = (memoryKey) => {
  return request.delete("/admin/ai/session/delete", { params: { memoryKey } });
};

// ==================== 学习规划管理 ====================

export const studyPlanList = (params) => {
  return request.get("/admin/ai/studyPlan/list", { params });
};

export const studyPlanTaskUpdate = (params) => {
  return request.put("/admin/ai/studyPlan/task/update", null, { params });
};

export const studyPlanTaskDelete = (params) => {
  return request.delete("/admin/ai/studyPlan/task/delete", { params });
};

export const studyPlanDelete = (params) => {
  return request.delete("/admin/ai/studyPlan/plan/delete", { params });
};
