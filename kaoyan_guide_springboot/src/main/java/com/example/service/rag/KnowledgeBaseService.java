package com.example.service.rag;

import com.example.entity.KbFile;
import com.github.pagehelper.PageInfo;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

public interface KnowledgeBaseService {

    KbFile uploadAndIngest(MultipartFile file, String title, String businessType, String remark, Long createBy);

    PageInfo<KbFile> selectPage(KbFile query, Integer pageNum, Integer pageSize);

    KbFile selectById(Long id);

    void reindexById(Long id);

    int reindexAll(String businessType, Boolean onlySuccess);

    Map<String, Object> deleteById(Long id);
}
