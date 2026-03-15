package com.example.service.impl;

import cn.hutool.core.io.FileUtil;
import com.example.entity.KnowledgeDocument;
import com.example.mapper.KnowledgeDocumentMapper;
import com.example.service.KnowledgeBaseService;
import com.example.service.rag.KnowledgeIngestService;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

@Service
public class KnowledgeBaseServiceImpl implements KnowledgeBaseService {

    private static final String STATUS_PENDING = "PENDING";
    private static final String STATUS_SUCCESS = "SUCCESS";

    @Value("${fileBaseUrl:}")
    private String fileBaseUrl;

    @Value("${app.knowledge-base.upload-dir:}")
    private String knowledgeUploadDir;

    @Resource
    private KnowledgeDocumentMapper knowledgeDocumentMapper;

    @Resource
    private KnowledgeIngestService knowledgeIngestService;

    @Override
    public KnowledgeDocument uploadAndIngest(MultipartFile file, String title, String businessType, String remark, Long createBy) {
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
        KnowledgeDocument document = new KnowledgeDocument();
        document.setTitle(title.trim());
        document.setFileName(originalFileName);
        document.setFilePath(filePath);
        document.setFileType(fileType);
        document.setBusinessType(businessType);
        document.setStatus(STATUS_PENDING);
        document.setChunkCount(0);
        document.setErrorMessage("");
        document.setRemark(remark);
        document.setCreateBy(createBy);
        knowledgeDocumentMapper.insert(document);

        KnowledgeDocument updating = new KnowledgeDocument();
        updating.setId(document.getId());
        updating.setFileUrl(fileBaseUrl + "/knowledge-base/download/" + document.getId());
        knowledgeDocumentMapper.updateById(updating);

        KnowledgeDocument saved = knowledgeDocumentMapper.selectById(document.getId());
        knowledgeIngestService.ingest(saved);
        return knowledgeDocumentMapper.selectById(document.getId());
    }

    @Override
    public PageInfo<KnowledgeDocument> selectPage(KnowledgeDocument query, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<KnowledgeDocument> list = knowledgeDocumentMapper.selectPage(query);
        return PageInfo.of(list);
    }

    @Override
    public KnowledgeDocument selectById(Long id) {
        return knowledgeDocumentMapper.selectById(id);
    }

    @Override
    public void reindexById(Long id) {
        KnowledgeDocument document = knowledgeDocumentMapper.selectById(id);
        if (document == null) {
            throw new RuntimeException("文档不存在");
        }
        knowledgeIngestService.deleteDocumentVectors(id);
        knowledgeIngestService.ingest(document);
    }

    @Override
    public int reindexAll(String businessType, Boolean onlySuccess) {
        String status = Boolean.TRUE.equals(onlySuccess) ? STATUS_SUCCESS : null;
        List<KnowledgeDocument> documents = knowledgeDocumentMapper.selectByCondition(businessType, status);
        for (KnowledgeDocument document : documents) {
            knowledgeIngestService.deleteDocumentVectors(document.getId());
            knowledgeIngestService.ingest(document);
        }
        return documents.size();
    }

    @Override
    public void deleteById(Long id) {
        KnowledgeDocument document = knowledgeDocumentMapper.selectById(id);
        if (document == null) {
            return;
        }
        knowledgeIngestService.deleteDocumentVectors(id);
        if (document.getFilePath() != null && !document.getFilePath().isBlank() && FileUtil.exist(document.getFilePath())) {
            FileUtil.del(document.getFilePath());
        }
        knowledgeDocumentMapper.deleteById(id);
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
}
