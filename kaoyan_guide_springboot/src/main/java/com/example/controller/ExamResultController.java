package com.example.controller;

import cn.hutool.poi.excel.ExcelUtil;
import cn.hutool.poi.excel.ExcelWriter;
import com.example.entity.Account;
import com.example.entity.ExamResult;
import com.example.service.ExamResultService;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletResponse;
import java.io.ByteArrayOutputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/exam")
public class ExamResultController {

    private final ExamResultService service;

    public ExamResultController(ExamResultService service) {
        this.service = service;
    }

    // ==================== 保存成绩（扩展 questionSource / simulationMode）====================
    @PostMapping("/saveResult")
    public Map<String, Object> saveResult(@RequestBody Map<String, Object> payload) {
        Map<String, Object> response = new HashMap<>();
        try {
            Account currentUser = TokenUtils.getCurrentUser();
            Long userId = currentUser.getId().longValue();

            String subject = (String) payload.get("subject");
            String questionSource = (String) payload.get("questionSource");
            String simulationMode = (String) payload.get("simulationMode");
            Number scoreNum = (Number) payload.get("score");
            Number durationNum = (Number) payload.get("duration");

            Integer score = scoreNum != null ? scoreNum.intValue() : null;
            Integer duration = durationNum != null ? durationNum.intValue() : null;

            if (subject == null || questionSource == null || questionSource.isBlank()
                    || score == null || duration == null) {
                response.put("code", "400");
                response.put("msg", "缺少参数，subject / questionSource / score / duration 均为必填");
                return response;
            }

            ExamResult result = new ExamResult();
            result.setUserId(userId);
            result.setSubject(subject);
            result.setQuestionSource(questionSource);
            result.setScore(score);
            result.setDurationSeconds(duration);
            result.setSimulationMode(simulationMode != null ? simulationMode : "演示模式");
            result.setCreateTime(LocalDateTime.now());

            service.saveResult(result);

            response.put("code", "200");
            response.put("msg", "保存成功");
        } catch (Exception e) {
            e.printStackTrace();
            response.put("code", "500");
            response.put("msg", "服务器错误");
        }
        return response;
    }

    // ==================== 列表接口（兼容近五次页，校验当前用户）====================
    @GetMapping("/list")
    public Map<String, Object> list(@RequestParam(required = false) Long userId) {
        Map<String, Object> response = new HashMap<>();
        try {
            Account currentUser = TokenUtils.getCurrentUser();
            Long currentUserId = currentUser.getId().longValue();
            // 忽略前端传来的 userId，始终使用当前登录用户
            List<ExamResult> results = service.getUserResults(currentUserId);
            response.put("code", "200");
            response.put("msg", "查询成功");
            response.put("data", results);
        } catch (Exception e) {
            e.printStackTrace();
            response.put("code", "500");
            response.put("msg", "服务器错误");
        }
        return response;
    }

    // ==================== 分页历史记录接口 ====================
    @GetMapping("/history")
    public Map<String, Object> history(
            @RequestParam(defaultValue = "1") int pageNum,
            @RequestParam(defaultValue = "10") int pageSize) {
        Map<String, Object> response = new HashMap<>();
        try {
            Account currentUser = TokenUtils.getCurrentUser();
            Long userId = currentUser.getId().longValue();
            PageInfo<ExamResult> pageInfo = service.getHistory(userId, pageNum, pageSize);
            response.put("code", "200");
            response.put("msg", "查询成功");
            response.put("data", pageInfo.getList());
            response.put("total", pageInfo.getTotal());
        } catch (Exception e) {
            e.printStackTrace();
            response.put("code", "500");
            response.put("msg", "服务器错误");
        }
        return response;
    }

    // ==================== 编辑单条记录 ====================
    @PutMapping("/update")
    public Map<String, Object> update(@RequestBody ExamResult examResult) {
        Map<String, Object> response = new HashMap<>();
        try {
            Account currentUser = TokenUtils.getCurrentUser();
            Long userId = currentUser.getId().longValue();
            // 强制使用当前登录用户，防止越权
            examResult.setUserId(userId);

            boolean ok = service.update(examResult);
            if (ok) {
                response.put("code", "200");
                response.put("msg", "更新成功");
            } else {
                response.put("code", "400");
                response.put("msg", "记录不存在或无权修改");
            }
        } catch (Exception e) {
            e.printStackTrace();
            response.put("code", "500");
            response.put("msg", "服务器错误");
        }
        return response;
    }

    // ==================== 导出 xlsx ====================
    @GetMapping("/export")
    public void export(HttpServletResponse response) throws Exception {
        Account currentUser = TokenUtils.getCurrentUser();
        Long userId = currentUser.getId().longValue();
        List<ExamResult> list = service.getUserResults(userId);

        // 构建行数据
        List<List<Object>> rows = new ArrayList<>();
        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        for (ExamResult r : list) {
            List<Object> row = new ArrayList<>();
            row.add(r.getSubject());
            row.add(r.getQuestionSource() != null && !r.getQuestionSource().isBlank()
                    ? r.getQuestionSource() : "-");
            row.add(r.getScore());
            row.add(formatDuration(r.getDurationSeconds()));
            row.add(r.getSimulationMode() != null ? r.getSimulationMode() : "-");
            row.add(r.getCreateTime() != null ? r.getCreateTime().format(fmt) : "-");
            rows.add(row);
        }

        ExcelWriter writer = ExcelUtil.getWriter(true);
        writer.addHeaderAlias("科目", "科目");
        List<String> headers = List.of("科目", "试题出处", "成绩", "用时", "模拟模式", "提交时间");
        writer.writeHeadRow(headers);
        writer.write(rows);

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        writer.flush(out, true);
        writer.close();

        String filename = URLEncoder.encode("考场模拟历史记录.xlsx", StandardCharsets.UTF_8);
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + filename);
        response.getOutputStream().write(out.toByteArray());
        response.getOutputStream().flush();
    }

    private String formatDuration(Integer seconds) {
        if (seconds == null) return "-";
        int h = seconds / 3600;
        int m = (seconds % 3600) / 60;
        int s = seconds % 60;
        if (h > 0) return String.format("%02d:%02d:%02d", h, m, s);
        return String.format("%02d:%02d", m, s);
    }
}

