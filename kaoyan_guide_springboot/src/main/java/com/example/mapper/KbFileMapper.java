package com.example.mapper;

import com.example.entity.KbFile;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface KbFileMapper {

    int insert(KbFile kbFile);

    int updateById(KbFile kbFile);

    int deleteById(@Param("id") Long id);

    KbFile selectById(@Param("id") Long id);

    KbFile selectByHash(@Param("fileHash") String fileHash);

    List<KbFile> selectPage(KbFile query);

    List<KbFile> selectByCondition(@Param("businessType") String businessType,
                                   @Param("status") String status);
}
