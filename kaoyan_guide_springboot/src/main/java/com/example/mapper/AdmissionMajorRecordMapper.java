package com.example.mapper;

import com.example.entity.AdmissionMajorRecord;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface AdmissionMajorRecordMapper {

    int insert(AdmissionMajorRecord record);

    int updateById(AdmissionMajorRecord record);

    int updateReviewStatus(@Param("id") Long id,
                           @Param("reviewStatus") String reviewStatus,
                           @Param("reviewComment") String reviewComment);

    AdmissionMajorRecord selectById(@Param("id") Long id);

    List<AdmissionMajorRecord> selectPage(AdmissionMajorRecord query);
}
