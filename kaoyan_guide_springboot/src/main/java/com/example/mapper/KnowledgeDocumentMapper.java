package com.example.mapper;

import com.example.entity.KnowledgeDocument;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface KnowledgeDocumentMapper {

    int insert(KnowledgeDocument knowledgeDocument);

    int updateById(KnowledgeDocument knowledgeDocument);

    int deleteById(@Param("id") Long id);

    KnowledgeDocument selectById(@Param("id") Long id);

    List<KnowledgeDocument> selectPage(KnowledgeDocument query);

    List<KnowledgeDocument> selectByCondition(@Param("businessType") String businessType,
                                              @Param("status") String status);
}
