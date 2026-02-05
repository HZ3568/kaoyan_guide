package com.example.entity;


/**
 * 大学认证信息
*/
public class UniversityCertification {
    /** 主键ID */
    private Integer id;
    /** 大学IDId */
    private Integer universityId;
    /** 学校代码 */
    private String universityCode;
    /** 办学许可证 */
    private String licenseImg;
    /** 招生资格认证 */
    private String qualificationsImg;
    /** 认证状态 */
    private String status;
    /** 拒绝理由 */
    private String refuseReason;
    /** 创建时间 */
    private String time;
    private String universityName;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getUniversityId() {
        return universityId;
    }

    public void setUniversityId(Integer universityId) {
        this.universityId = universityId;
    }

    public String getUniversityName() {
        return universityName;
    }

    public void setUniversityName(String universityName) {
        this.universityName = universityName;
    }

    public String getUniversityCode() {
        return universityCode;
    }

    public void setUniversityCode(String universityCode) {
        this.universityCode = universityCode;
    }

    public String getLicenseImg() {
        return licenseImg;
    }

    public void setLicenseImg(String licenseImg) {
        this.licenseImg = licenseImg;
    }

    public String getQualificationsImg() {
        return qualificationsImg;
    }

    public void setQualificationsImg(String qualificationsImg) {
        this.qualificationsImg = qualificationsImg;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getRefuseReason() {
        return refuseReason;
    }

    public void setRefuseReason(String refuseReason) {
        this.refuseReason = refuseReason;
    }

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }

}