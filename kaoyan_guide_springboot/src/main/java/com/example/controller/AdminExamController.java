package com.example.controller;

import cn.hutool.poi.excel.ExcelUtil;
import cn.hutool.poi.excel.ExcelWriter;
import com.example.common.Result;
import com.example.service.AdminExamService;
import com.github.pagehelper.PageInfo;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.bind.annotation.*;

import java.io.ByteArrayOutputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/admin/exam")
public class AdminExamController {

    private final AdminExamService service;

    public AdminExamController(AdminExamService service) {
        this.service = service;
    }

    /**
     * 分页查询所有用户的考试记录
     */
    @GetMapping("/list")
    public Result list(
            @RequestParam(defaultValue = "1") int pageNum,
            @RequestParam(defaultValue = "10") int pageSize) {
        PageInfo<Map<String, Object>> page = service.selectAllResults(pageNum, pageSize);
        return Result.success(page);
    }

    /**
     * 导出所有考试记录为 Excel
     */
    @GetMapping("/export")
    public void export(HttpServletResponse response) throws Exception {
        PageInfo<Map<String, Object>> page = service.selectAllResults(1, 10000);
        List<Map<String, Object>> list = page.getList();

        DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        ExcelWriter writer = ExcelUtil.getWriter(true);
        writer.addHeaderAlias("userId", "用户ID");
        writer.addHeaderAlias("userName", "用户名");
        writer.addHeaderAlias("subject", "科目");
        writer.addHeaderAlias("questionSource", "试题出处");
        writer.addHeaderAlias("score", "成绩");
        writer.addHeaderAlias("durationSeconds", "用时(秒)");
        writer.addHeaderAlias("simulationMode", "模拟模式");
        writer.addHeaderAlias("createTime", "提交时间");

        for (Map<String, Object> row : list) {
            Object createTime = row.get("createTime");
            if (createTime != null) {
                row.put("createTime", createTime.toString().replace("T", " "));
            }
        }

        writer.write(list, true);

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        writer.flush(out, true);
        writer.close();

        String filename = URLEncoder.encode("考试数据记录.xlsx", StandardCharsets.UTF_8);
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + filename);
        response.getOutputStream().write(out.toByteArray());
        response.getOutputStream().flush();
    }
}
