package com.example.controller;

import com.example.common.Result;
import com.example.entity.AdmissionMajorRecord;
import com.example.entity.AdmissionOcrBatch;
import com.example.service.AdmissionOcrService;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/admission-ocr")
public class AdmissionOcrController {

    @Resource
    private AdmissionOcrService admissionOcrService;

    /**
     * 分页查询OCR专业记录
     */
    @GetMapping("/records/selectPage")
    public Result selectRecordPage(AdmissionMajorRecord query,
                                   @RequestParam(defaultValue = "1") Integer pageNum,
                                   @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<AdmissionMajorRecord> page = admissionOcrService.selectRecordPage(query, pageNum, pageSize);
        return Result.success(page);
    }

    /**
     * 根据ID查询OCR专业记录详情
     */
    @GetMapping("/records/selectById/{id}")
    public Result selectRecordById(@PathVariable Long id) {
        AdmissionMajorRecord record = admissionOcrService.selectRecordById(id);
        return Result.success(record);
    }

    /**
     * 修改OCR专业记录字段
     */
    @PutMapping("/records/update")
    public Result updateRecord(@RequestBody AdmissionMajorRecord record) {
        admissionOcrService.updateRecord(record);
        return Result.success();
    }

    /**
     * 审核通过
     */
    @PutMapping("/records/approve/{id}")
    public Result approveRecord(@PathVariable Long id) {
        admissionOcrService.approveRecord(id);
        return Result.success();
    }

    /**
     * 审核驳回
     */
    @PutMapping("/records/reject/{id}")
    public Result rejectRecord(@PathVariable Long id,
                               @RequestParam(value = "reviewComment", required = false) String reviewComment,
                               @RequestBody(required = false) Map<String, Object> body) {
        if ((reviewComment == null || reviewComment.isBlank()) && body != null) {
            Object bodyComment = body.get("reviewComment");
            reviewComment = bodyComment == null ? null : String.valueOf(bodyComment);
        }
        admissionOcrService.rejectRecord(id, reviewComment);
        return Result.success();
    }

    /**
     * 分页查询OCR批次
     */
    @GetMapping("/batches/selectPage")
    public Result selectBatchPage(AdmissionOcrBatch query,
                                  @RequestParam(defaultValue = "1") Integer pageNum,
                                  @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<AdmissionOcrBatch> page = admissionOcrService.selectBatchPage(query, pageNum, pageSize);
        return Result.success(page);
    }

    /**
     * 根据ID查询OCR批次详情
     */
    @GetMapping("/batches/selectById/{id}")
    public Result selectBatchById(@PathVariable Long id) {
        AdmissionOcrBatch batch = admissionOcrService.selectBatchById(id);
        return Result.success(batch);
    }
}
