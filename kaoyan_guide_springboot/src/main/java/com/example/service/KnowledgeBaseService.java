package com.example.service;

import com.example.entity.KnowledgeDocument;
import com.github.pagehelper.PageInfo;
import org.springframework.web.multipart.MultipartFile;

public interface KnowledgeBaseService {

    KnowledgeDocument uploadAndIngest(MultipartFile file, String title, String businessType, String remark, Long createBy);

    PageInfo<KnowledgeDocument> selectPage(KnowledgeDocument query, Integer pageNum, Integer pageSize);

    KnowledgeDocument selectById(Long id);

    void reindexById(Long id);

    int reindexAll(String businessType, Boolean onlySuccess);

    void deleteById(Long id);
}
