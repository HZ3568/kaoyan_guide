package com.example.mapper;

import com.example.entity.KbContent;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface KbContentMapper {

    int insertBatch(@Param("list") List<KbContent> list);

    int deleteByFileId(@Param("fileId") Long fileId);

    List<KbContent> selectByFileId(@Param("fileId") Long fileId);
}
