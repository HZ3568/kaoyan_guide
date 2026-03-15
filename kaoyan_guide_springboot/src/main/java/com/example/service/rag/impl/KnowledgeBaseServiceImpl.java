package com.example.service.rag.impl;

import cn.hutool.crypto.digest.DigestUtil;
import cn.hutool.core.io.FileUtil;
import com.example.entity.KbFile;
import com.example.mapper.KbContentMapper;
import com.example.mapper.KbFileMapper;
import com.example.service.rag.KnowledgeBaseService;
import com.example.service.rag.KnowledgeIngestService;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;

@Service
public class KnowledgeBaseServiceImpl implements KnowledgeBaseService {

    private static final Logger log = LoggerFactory.getLogger(KnowledgeBaseServiceImpl.class);
    private static final String STATUS_UPLOADING = "UPLOADING";
    private static final String STATUS_INDEXED = "INDEXED";
    private static final String STATUS_FAILED = "FAILED";

    @Value("${fileBaseUrl:}")
    private String fileBaseUrl;

    @Value("${app.knowledge-base.upload-dir:}")
    private String knowledgeUploadDir;

    @Resource
    private KbFileMapper kbFileMapper;

    @Resource
    private KbContentMapper kbContentMapper;

    @Resource
    private KnowledgeIngestService knowledgeIngestService;

    @Override
    public KbFile uploadAndIngest(MultipartFile file, String title, String businessType, String remark, Long createBy) {
        validateUpload(file, title);
        String originalFileName = file.getOriginalFilename();
        String fileType = resolveFileType(originalFileName);
        ensureSupportedType(fileType);
        String storageDir = resolveStorageDir();
        FileUtil.mkdir(storageDir);
        String storedName = System.currentTimeMillis() + "-" + UUID.randomUUID().toString().replace("-", "")
                + "." + fileType;
        String filePath = storageDir + File.separator + storedName;
        try {
            file.transferTo(new File(filePath));
        } catch (Exception e) {
            throw new RuntimeException("文件保存失败");
        }

        KbFile kbFile = null;
        try {
            String fileHash = DigestUtil.sha256Hex(new File(filePath));
            KbFile exists = kbFileMapper.selectByHash(fileHash);
            if (exists != null) {
                FileUtil.del(filePath);
                throw new RuntimeException("文件已存在，不允许重复上传");
            }
            kbFile = new KbFile();
            kbFile.setTitle(title.trim());
            kbFile.setFileName(originalFileName);
            kbFile.setFilePath(filePath);
            kbFile.setFileType(fileType);
            kbFile.setBusinessType(businessType);
            kbFile.setFileHash(fileHash);
            kbFile.setFileSize(file.getSize());
            kbFile.setStatus(STATUS_UPLOADING);
            kbFile.setSegmentCount(0);
            kbFile.setErrorMessage("");
            kbFile.setRemark(remark);
            kbFile.setCreateBy(createBy);
            kbFileMapper.insert(kbFile);

            KbFile updating = new KbFile();
            updating.setId(kbFile.getId());
            updating.setFileUrl(fileBaseUrl + "/knowledge-base/download/" + kbFile.getId());
            updating.setRedisPrefix("kb:file:" + kbFile.getId());
            kbFileMapper.updateById(updating);

            KbFile saved = kbFileMapper.selectById(kbFile.getId());
            knowledgeIngestService.ingest(saved);
            return kbFileMapper.selectById(kbFile.getId());
        } catch (RuntimeException e) {
            if (kbFile == null && FileUtil.exist(filePath)) {
                FileUtil.del(filePath);
            }
            if (kbFile != null && kbFile.getId() != null) {
                updateFailedStatus(kbFile.getId(), e.getMessage());
            }
            throw e;
        } catch (Exception e) {
            log.error("知识库上传失败，filePath={}", filePath, e);
            if (kbFile == null && FileUtil.exist(filePath)) {
                FileUtil.del(filePath);
            }
            if (kbFile != null && kbFile.getId() != null) {
                updateFailedStatus(kbFile.getId(), simplifyError(e));
            }
            throw new RuntimeException("上传入库失败：" + simplifyError(e));
        }
    }

    @Override
    public PageInfo<KbFile> selectPage(KbFile query, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<KbFile> list = kbFileMapper.selectPage(query);
        return PageInfo.of(list);
    }

    @Override
    public KbFile selectById(Long id) {
        return kbFileMapper.selectById(id);
    }

    @Override
    public void reindexById(Long id) {
        KbFile file = kbFileMapper.selectById(id);
        if (file == null) {
            throw new RuntimeException("文档不存在");
        }
        knowledgeIngestService.deleteFileVectors(id);
        kbContentMapper.deleteByFileId(id);
        knowledgeIngestService.ingest(file);
    }

    @Override
    public int reindexAll(String businessType, Boolean onlySuccess) {
        String status = Boolean.TRUE.equals(onlySuccess) ? STATUS_INDEXED : null;
        List<KbFile> files = kbFileMapper.selectByCondition(businessType, status);
        for (KbFile file : files) {
            knowledgeIngestService.deleteFileVectors(file.getId());
            kbContentMapper.deleteByFileId(file.getId());
            knowledgeIngestService.ingest(file);
        }
        return files.size();
    }

    @Override
    public Map<String, Object> deleteById(Long id) {
        KbFile file = kbFileMapper.selectById(id);
        if (file == null) {
            throw new RuntimeException("文档不存在");
        }
        boolean redisDeleted;
        try {
            redisDeleted = knowledgeIngestService.deleteFileVectors(id);
        } catch (Exception e) {
            log.error("删除知识库Redis向量失败，fileId={}", id, e);
            throw new RuntimeException("Redis向量删除失败：" + simplifyError(e));
        }
        int contentDeletedCount = kbContentMapper.deleteByFileId(id);
        boolean dbDeleted = kbFileMapper.deleteById(id) > 0;
        boolean localFileDeleted = true;
        if (file.getFilePath() != null && !file.getFilePath().isBlank() && FileUtil.exist(file.getFilePath())) {
            localFileDeleted = FileUtil.del(file.getFilePath());
        }
        Map<String, Object> result = new HashMap<>();
        result.put("fileId", id);
        result.put("redisDeleted", redisDeleted);
        result.put("contentDeleted", true);
        result.put("contentDeletedCount", contentDeletedCount);
        result.put("dbDeleted", dbDeleted);
        result.put("localFileDeleted", localFileDeleted);
        return result;
    }

    private void validateUpload(MultipartFile file, String title) {
        if (file == null || file.isEmpty()) {
            throw new RuntimeException("请上传文件");
        }
        if (title == null || title.trim().isEmpty()) {
            throw new RuntimeException("请输入文档标题");
        }
    }

    private String resolveStorageDir() {
        if (knowledgeUploadDir != null && !knowledgeUploadDir.isBlank()) {
            return new File(knowledgeUploadDir).getAbsoluteFile().toPath().normalize().toString();
        }
        return new File(System.getProperty("user.dir"), "files" + File.separator + "knowledge-base")
                .getAbsoluteFile().toPath().normalize().toString();
    }

    private String resolveFileType(String fileName) {
        if (fileName == null || !fileName.contains(".")) {
            return "";
        }
        return fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase(Locale.ROOT);
    }

    private void ensureSupportedType(String fileType) {
        if ("pdf".equals(fileType) || "txt".equals(fileType) || "md".equals(fileType)) {
            return;
        }
        throw new RuntimeException("仅支持 PDF/TXT/MD 文件");
    }

    private void updateFailedStatus(Long fileId, String errorMessage) {
        KbFile updating = new KbFile();
        updating.setId(fileId);
        updating.setStatus(STATUS_FAILED);
        updating.setErrorMessage(errorMessage == null ? "" : errorMessage);
        kbFileMapper.updateById(updating);
    }

    private String simplifyError(Exception e) {
        String message = e == null ? null : e.getMessage();
        if (message == null || message.isBlank()) {
            return "未知错误";
        }
        String normalized = message.replace("\r", " ").replace("\n", " ").trim();
        if (normalized.length() > 200) {
            return normalized.substring(0, 200);
        }
        return normalized;
    }
}
