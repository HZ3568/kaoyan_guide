package com.example.entity;


/**
 * 学生认证信息
*/
public class UserCertification {
    /** 主键ID */
    private Integer id;
    /** 学生IDId */
    private Integer userId;
    /** 考生号 */
    private String candidateNumber;
    /** 准考证号 */
    private String examinationNumber;
    /** 身份证号 */
    private String identityNumber;
    /** 身份证照片 */
    private String identityImg;
    /** 认证状态 */
    private String status;
    /** 拒绝理由 */
    private String refuseReason;
    /** 创建时间 */
    private String time;
    private String userName;
    private Integer score;
    private Integer ranking;
    private Integer areasId;
    private String areasName;

    public Integer getScore() {
        return score;
    }

    public void setScore(Integer score) {
        this.score = score;
    }

    public Integer getRanking() {
        return ranking;
    }

    public void setRanking(Integer ranking) {
        this.ranking = ranking;
    }

    public Integer getAreasId() {
        return areasId;
    }

    public void setAreasId(Integer areasId) {
        this.areasId = areasId;
    }

    public String getAreasName() {
        return areasName;
    }

    public void setAreasName(String areasName) {
        this.areasName = areasName;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public String getCandidateNumber() {
        return candidateNumber;
    }

    public void setCandidateNumber(String candidateNumber) {
        this.candidateNumber = candidateNumber;
    }

    public String getExaminationNumber() {
        return examinationNumber;
    }

    public void setExaminationNumber(String examinationNumber) {
        this.examinationNumber = examinationNumber;
    }

    public String getIdentityNumber() {
        return identityNumber;
    }

    public void setIdentityNumber(String identityNumber) {
        this.identityNumber = identityNumber;
    }

    public String getIdentityImg() {
        return identityImg;
    }

    public void setIdentityImg(String identityImg) {
        this.identityImg = identityImg;
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