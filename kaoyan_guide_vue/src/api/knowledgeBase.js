import request from "@/utils/request.js";

export const knowledgeBaseUpload = (formData) => {
  return request.post("/knowledge-base/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const knowledgeBasePage = (params) => {
  return request.get("/knowledge-base/page", { params });
};

export const knowledgeBaseDetail = (id) => {
  return request.get(`/knowledge-base/${id}`);
};

export const knowledgeBaseReindex = (id) => {
  return request.post(`/knowledge-base/reindex/${id}`);
};

export const knowledgeBaseReindexAll = (params) => {
  return request.post("/knowledge-base/reindex-all", null, { params });
};

export const knowledgeBaseDelete = (id) => {
  return request.delete(`/knowledge-base/${id}`);
};

export const knowledgeBaseDownload = (id) => {
  return request.get(`/knowledge-base/download/${id}`, {
    responseType: "blob",
    returnRawResponse: true,
  });
};
