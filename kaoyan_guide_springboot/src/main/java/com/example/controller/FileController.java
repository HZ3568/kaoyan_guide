package com.example.controller;

import cn.hutool.core.collection.CollUtil;
import cn.hutool.core.io.FileUtil;
import cn.hutool.core.lang.Dict;
import cn.hutool.core.util.StrUtil;
import com.example.common.Result;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.util.UriUtils;

import java.io.File;
import java.io.OutputStream;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@RestController
@RequestMapping("/files")
public class FileController {

    private static final Logger log = LoggerFactory.getLogger(FileController.class);

    private static final String FILE_DIRECTORY_NAME = "files";

    @Value("${fileBaseUrl:}")
    private String fileBaseUrl;

    @Value("${file.upload-dir:}")
    private String uploadDir;

    /**
     * 文件上传
     */
    @PostMapping("/upload")
    public Result upload(MultipartFile file) {
        String originalFileName = file == null ? null : file.getOriginalFilename();
        try {
            if (file == null || file.isEmpty()) {
                return Result.error("文件为空");
            }
            String safeFileName = StrUtil.isBlank(originalFileName) ? "unknown" : new File(originalFileName).getName();
            String fileName = System.currentTimeMillis() + "-" + safeFileName;
            String primaryStorageDir = resolvePrimaryStorageDir();
            if (!FileUtil.isDirectory(primaryStorageDir)) {
                FileUtil.mkdir(primaryStorageDir);
            }
            FileUtil.writeBytes(file.getBytes(), primaryStorageDir + File.separator + fileName);
            String encodedFileName = UriUtils.encodePathSegment(fileName, StandardCharsets.UTF_8);
            String url = fileBaseUrl + "/files/download/" + encodedFileName;
            return Result.success(url);
        } catch (Exception e) {
            log.error("{}--文件上传失败", originalFileName, e);
            return Result.error("文件上传失败");
        }
    }

    /**
     * 获取文件
     */
    @GetMapping("/download/{fileName:.+}")
    public void download(@PathVariable String fileName, HttpServletResponse response) {
        try {
            if (StrUtil.isEmpty(fileName)) {
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                return;
            }
            String decodedFileName = URLDecoder.decode(fileName, StandardCharsets.UTF_8);
            String realFilePath = resolveExistingFilePath(decodedFileName);
            if (StrUtil.isBlank(realFilePath)) {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                log.warn("文件下载失败：{}，未找到文件", decodedFileName);
                return;
            }
            String encodedFileName = URLEncoder.encode(decodedFileName, StandardCharsets.UTF_8).replaceAll("\\+", "%20");
            response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + encodedFileName);
            response.setContentType("application/octet-stream");
            byte[] bytes = FileUtil.readBytes(realFilePath);
            OutputStream os = response.getOutputStream();
            os.write(bytes);
            os.flush();
            os.close();
        } catch (Exception e) {
            log.warn("文件下载失败：{}", fileName, e);
        }
    }

    /**
     * wang-editor编辑器文件上传接口
     */
    @PostMapping("/wang/upload")
    public Map<String, Object> wangEditorUpload(MultipartFile file) {
        String flag = System.currentTimeMillis() + "";
        String fileName = file.getOriginalFilename();
        try {
            String primaryStorageDir = resolvePrimaryStorageDir();
            if (!FileUtil.isDirectory(primaryStorageDir)) {
                FileUtil.mkdir(primaryStorageDir);
            }
            FileUtil.writeBytes(file.getBytes(), primaryStorageDir + File.separator + flag + "-" + fileName);
            System.out.println(fileName + "--上传成功");
            Thread.sleep(1L);
        } catch (Exception e) {
            System.err.println(fileName + "--文件上传失败");
        }
        String http = fileBaseUrl + "/files/download/";
        Map<String, Object> resMap = new HashMap<>();
        // wangEditor上传图片成功后， 需要返回的参数
        resMap.put("errno", 0);
        String encodedFileName = UriUtils.encodePathSegment(flag + "-" + fileName, StandardCharsets.UTF_8);
        resMap.put("data", CollUtil.newArrayList(Dict.create().set("url", http + encodedFileName)));
        return resMap;
    }

    private String resolvePrimaryStorageDir() {
        if (StrUtil.isNotBlank(uploadDir)) {
            return Paths.get(uploadDir).toAbsolutePath().normalize().toString();
        }
        return Paths.get(System.getProperty("user.dir"), FILE_DIRECTORY_NAME).toAbsolutePath().normalize().toString();
    }

    private String resolveExistingFilePath(String fileName) {
        for (String dir : resolveCandidateStorageDirs()) {
            String fullPath = dir + File.separator + fileName;
            if (FileUtil.exist(fullPath)) {
                return fullPath;
            }
        }
        return null;
    }

    private List<String> resolveCandidateStorageDirs() {
        Set<String> directories = new LinkedHashSet<>();
        String primaryDir = resolvePrimaryStorageDir();
        directories.add(primaryDir);
        Path userDirPath = Paths.get(System.getProperty("user.dir")).toAbsolutePath().normalize();
        directories.add(userDirPath.resolve("kaoyan_guide_springboot").resolve(FILE_DIRECTORY_NAME).normalize().toString());
        if (userDirPath.getParent() != null) {
            directories.add(userDirPath.getParent().resolve("kaoyan_guide_springboot").resolve(FILE_DIRECTORY_NAME).normalize().toString());
        }
        return directories.stream().toList();
    }
}
