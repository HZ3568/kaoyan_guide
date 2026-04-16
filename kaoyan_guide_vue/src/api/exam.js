import request from "@/utils/request.js";

export const examDataList = (params) => {
  return request.get("/admin/exam/list", { params });
};

export const examDataExport = () => {
  return request.get("/admin/exam/export", {
    responseType: "blob",
    returnRawResponse: true,
  });
};
