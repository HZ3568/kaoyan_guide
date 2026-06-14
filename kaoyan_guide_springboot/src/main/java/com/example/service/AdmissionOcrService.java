package com.example.service;

import com.example.common.enums.AdmissionReviewStatus;
import com.example.common.enums.ResultCodeEnum;
import com.example.entity.AdmissionMajorRecord;
import com.example.entity.AdmissionOcrBatch;
import com.example.exception.CustomException;
import com.example.mapper.AdmissionMajorRecordMapper;
import com.example.mapper.AdmissionOcrBatchMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.List;
import java.util.regex.Pattern;

@Service
public class AdmissionOcrService {

    private static final Pattern SHA256_PATTERN = Pattern.compile("^[a-fA-F0-9]{64}$");
    private static final Pattern SCORE_LINE_PATTERN = Pattern.compile(".*\\d{2,3}.*");
    private static final BigDecimal ZERO = BigDecimal.ZERO;
    private static final BigDecimal ONE = BigDecimal.ONE;
    private static final BigDecimal MAX_SCORE = new BigDecimal("500");

    @Resource
    private AdmissionOcrBatchMapper admissionOcrBatchMapper;

    @Resource
    private AdmissionMajorRecordMapper admissionMajorRecordMapper;

    public PageInfo<AdmissionMajorRecord> selectRecordPage(AdmissionMajorRecord query,
                                                           Integer pageNum,
                                                           Integer pageSize) {
        if (query != null && query.getReviewStatus() != null && !query.getReviewStatus().isBlank()) {
            String reviewStatus = AdmissionReviewStatus.normalize(query.getReviewStatus());
            if (reviewStatus == null) {
                fail("审核状态不合法");
            }
            query.setReviewStatus(reviewStatus);
        }
        PageHelper.startPage(normalizePageNum(pageNum), normalizePageSize(pageSize));
        List<AdmissionMajorRecord> list = admissionMajorRecordMapper.selectPage(query);
        return PageInfo.of(list);
    }

    public AdmissionMajorRecord selectRecordById(Long id) {
        requireId(id);
        AdmissionMajorRecord record = admissionMajorRecordMapper.selectById(id);
        if (record == null) {
            fail("专业记录不存在");
        }
        return record;
    }

    public void updateRecord(AdmissionMajorRecord record) {
        if (record == null || record.getId() == null) {
            fail("记录ID不能为空");
        }
        AdmissionMajorRecord existing = admissionMajorRecordMapper.selectById(record.getId());
        if (existing == null) {
            fail("专业记录不存在");
        }
        normalizeUpdateText(record);
        validateRecordUpdate(record, existing);
        admissionMajorRecordMapper.updateById(record);
    }

    public void approveRecord(Long id) {
        updateReviewStatus(id, AdmissionReviewStatus.APPROVED.name(), null);
    }

    public void rejectRecord(Long id, String reviewComment) {
        if (reviewComment == null || reviewComment.trim().isEmpty()) {
            fail("驳回原因不能为空");
        }
        updateReviewStatus(id, AdmissionReviewStatus.REJECTED.name(), reviewComment.trim());
    }

    public PageInfo<AdmissionOcrBatch> selectBatchPage(AdmissionOcrBatch query,
                                                       Integer pageNum,
                                                       Integer pageSize) {
        PageHelper.startPage(normalizePageNum(pageNum), normalizePageSize(pageSize));
        List<AdmissionOcrBatch> list = admissionOcrBatchMapper.selectPage(query);
        return PageInfo.of(list);
    }

    public AdmissionOcrBatch selectBatchById(Long id) {
        requireId(id);
        AdmissionOcrBatch batch = admissionOcrBatchMapper.selectById(id);
        if (batch == null) {
            fail("OCR批次不存在");
        }
        return batch;
    }

    private void updateReviewStatus(Long id, String reviewStatus, String reviewComment) {
        requireId(id);
        AdmissionMajorRecord record = admissionMajorRecordMapper.selectById(id);
        if (record == null) {
            fail("专业记录不存在");
        }
        admissionMajorRecordMapper.updateReviewStatus(id, reviewStatus, reviewComment);
    }

    private void validateRecordUpdate(AdmissionMajorRecord record, AdmissionMajorRecord existing) {
        requireNotBlankIfPresent(record.getSchoolName(), "学校名称不能为空");
        requireNotBlankIfPresent(record.getSchoolCode(), "学校代码不能为空");
        requireNotBlankIfPresent(record.getMajorName(), "专业名称不能为空");
        requireNotBlankIfPresent(record.getBatchNo(), "批次号不能为空");

        if (record.getReviewStatus() != null) {
            String reviewStatus = AdmissionReviewStatus.normalize(record.getReviewStatus());
            if (reviewStatus == null) {
                fail("审核状态不合法");
            }
            record.setReviewStatus(reviewStatus);
        }
        if (record.getScoreLine() != null && !record.getScoreLine().isBlank()
                && !SCORE_LINE_PATTERN.matcher(record.getScoreLine()).matches()) {
            fail("分数线格式异常");
        }
        if (record.getRetestCount() != null && record.getRetestCount() < 0) {
            fail("复试人数不能为负数");
        }
        if (record.getAdmittedCount() != null && record.getAdmittedCount() < 0) {
            fail("录取人数不能为负数");
        }
        if (record.getYear() != null && (record.getYear() < 2000 || record.getYear() > 2100)) {
            fail("年份格式异常");
        }
        if (record.getFileHash() != null && !record.getFileHash().isBlank()
                && !SHA256_PATTERN.matcher(record.getFileHash()).matches()) {
            fail("文件hash格式异常");
        }
        validateScore(record.getAvgScore(), "平均分");
        validateScore(record.getMinScore(), "最低分");
        validateScore(record.getMaxScore(), "最高分");
        validateConfidence(record.getConfidence());
        validateScoreRange(valueOrDefault(record.getMinScore(), existing.getMinScore()),
                valueOrDefault(record.getMaxScore(), existing.getMaxScore()));
    }

    private void validateScoreRange(BigDecimal minScore, BigDecimal maxScore) {
        if (minScore != null && maxScore != null && minScore.compareTo(maxScore) > 0) {
            fail("最低分不能大于最高分");
        }
    }

    private void validateScore(BigDecimal score, String fieldName) {
        if (score == null) {
            return;
        }
        if (score.compareTo(ZERO) < 0 || score.compareTo(MAX_SCORE) > 0) {
            fail(fieldName + "格式异常");
        }
    }

    private void validateConfidence(BigDecimal confidence) {
        if (confidence == null) {
            return;
        }
        if (confidence.compareTo(ZERO) < 0 || confidence.compareTo(ONE) > 0) {
            fail("置信度必须在0到1之间");
        }
    }

    private BigDecimal valueOrDefault(BigDecimal value, BigDecimal defaultValue) {
        return value != null ? value : defaultValue;
    }

    private void normalizeUpdateText(AdmissionMajorRecord record) {
        record.setBatchNo(trim(record.getBatchNo()));
        record.setSchoolName(trim(record.getSchoolName()));
        record.setSchoolCode(trim(record.getSchoolCode()));
        record.setCollegeName(trim(record.getCollegeName()));
        record.setMajorCode(trim(record.getMajorCode()));
        record.setMajorName(trim(record.getMajorName()));
        record.setResearchDirection(trim(record.getResearchDirection()));
        record.setExamSubjects(trim(record.getExamSubjects()));
        record.setScoreLine(trim(record.getScoreLine()));
        record.setSourceImage(trim(record.getSourceImage()));
        record.setFileHash(trim(record.getFileHash()));
        record.setIssues(trim(record.getIssues()));
        record.setReviewStatus(trim(record.getReviewStatus()));
        record.setReviewComment(trim(record.getReviewComment()));
    }

    private String trim(String value) {
        return value == null ? null : value.trim();
    }

    private void requireNotBlankIfPresent(String value, String message) {
        if (value != null && value.isBlank()) {
            fail(message);
        }
    }

    private void requireId(Long id) {
        if (id == null || id <= 0) {
            fail("ID不能为空");
        }
    }

    private int normalizePageNum(Integer pageNum) {
        if (pageNum == null || pageNum < 1) {
            return 1;
        }
        return pageNum;
    }

    private int normalizePageSize(Integer pageSize) {
        if (pageSize == null || pageSize < 1) {
            return 10;
        }
        return Math.min(pageSize, 100);
    }

    private void fail(String message) {
        throw new CustomException(ResultCodeEnum.PARAM_ERROR.code, message);
    }
}
