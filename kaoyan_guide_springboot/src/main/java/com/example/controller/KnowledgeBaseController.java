package com.example.controller;

import cn.hutool.core.io.FileUtil;
import com.example.common.Result;
import com.example.common.enums.RoleEnum;
import com.example.entity.Account;
import com.example.entity.KbFile;
import com.example.service.rag.KnowledgeBaseService;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.io.OutputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/knowledge-base")
public class KnowledgeBaseController {

    @Resource
    private KnowledgeBaseService knowledgeBaseService;

    @PostMapping("/upload")
    public Result upload(@RequestParam("file") MultipartFile file,
                         @RequestParam("title") String title,
                         @RequestParam(value = "businessType", required = false) String businessType,
                         @RequestParam(value = "remark", required = false) String remark) {
        try {
            Account account = requireAdmin();
            KbFile result = knowledgeBaseService.uploadAndIngest(file, title, businessType, remark, account.getId().longValue());
            return Result.success(result);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/page")
    public Result page(KbFile query,
                       @RequestParam(defaultValue = "1") Integer pageNum,
                       @RequestParam(defaultValue = "10") Integer pageSize) {
        requireAdmin();
        PageInfo<KbFile> page = knowledgeBaseService.selectPage(query, pageNum, pageSize);
        return Result.success(page);
    }

    @GetMapping("/{id}")
    public Result detail(@PathVariable Long id) {
        requireAdmin();
        KbFile file = knowledgeBaseService.selectById(id);
        if (file == null) {
            return Result.error("文档不存在");
        }
        return Result.success(file);
    }

    @PostMapping("/reindex/{id}")
    public Result reindex(@PathVariable Long id) {
        try {
            requireAdmin();
            knowledgeBaseService.reindexById(id);
            return Result.success();
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @PostMapping("/reindex-all")
    public Result reindexAll(@RequestParam(value = "businessType", required = false) String businessType,
                             @RequestParam(value = "onlySuccess", required = false, defaultValue = "true") Boolean onlySuccess) {
        try {
            requireAdmin();
            int count = knowledgeBaseService.reindexAll(businessType, onlySuccess);
            Map<String, Object> data = new HashMap<>();
            data.put("count", count);
            return Result.success(data);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public Result delete(@PathVariable Long id) {
        try {
            requireAdmin();
            return Result.success(knowledgeBaseService.deleteById(id));
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    @GetMapping("/download/{id}")
    public void download(@PathVariable Long id, HttpServletResponse response) {
        requireAdmin();
        KbFile file = knowledgeBaseService.selectById(id);
        if (file == null || file.getFilePath() == null || !FileUtil.exist(file.getFilePath())) {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            return;
        }
        try {
            String fileName = file.getFileName() == null ? "knowledge-file" : file.getFileName();
            String encodedFileName = URLEncoder.encode(fileName, StandardCharsets.UTF_8).replaceAll("\\+", "%20");
            response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + encodedFileName);
            response.setContentType("application/octet-stream");
            byte[] bytes = FileUtil.readBytes(file.getFilePath());
            OutputStream os = response.getOutputStream();
            os.write(bytes);
            os.flush();
            os.close();
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
        }
    }

    private Account requireAdmin() {
        Account currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null || currentUser.getRole() == null || !RoleEnum.ADMIN.name().equals(currentUser.getRole())) {
            throw new RuntimeException("无权限操作");
        }
        return currentUser;
    }
}
