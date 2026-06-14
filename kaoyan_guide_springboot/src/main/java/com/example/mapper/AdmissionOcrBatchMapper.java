package com.example.mapper;

import com.example.entity.AdmissionOcrBatch;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface AdmissionOcrBatchMapper {

    int insert(AdmissionOcrBatch batch);

    int updateById(AdmissionOcrBatch batch);

    AdmissionOcrBatch selectById(@Param("id") Long id);

    AdmissionOcrBatch selectByBatchNo(@Param("batchNo") String batchNo);

    List<AdmissionOcrBatch> selectPage(AdmissionOcrBatch query);
}
