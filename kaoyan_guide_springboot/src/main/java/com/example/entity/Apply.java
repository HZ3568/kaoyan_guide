package com.example.entity;


/**
 * 报考信息
*/
public class Apply {
    /** 主键ID */
    private Integer id;
    /** 学生IDId */
    private Integer userId;
    /** 第一学校Id */
    private Integer firstUniversityId;
    /** 第一专业Id */
    private Integer firstSpecialtysId;
    /** 第一志愿状态 */
    private String firstStatus;
    /** 第二学校Id */
    private Integer secondUniversityId;
    /** 第二专业Id */
    private Integer secondSpecialtysId;
    /** 第二志愿状态 */
    private String secondStatus;
    /** 第三学校Id */
    private Integer thirdUniversityId;
    /** 第三专业Id */
    private Integer thirdSpecialtysId;
    /** 第三志愿状态 */
    private String thirdStatus;
    /** 志愿状态 */
    private String status;
    /** 报考时间 */
    private String time;
    private String userName;
    private String firstUniversityName;
    private String firstSpecialtysName;
    private String secondUniversityName;
    private String secondSpecialtysName;
    private String thirdUniversityName;
    private String thirdSpecialtysName;
    private Integer score;
    private Integer ranking;
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

    public Integer getFirstUniversityId() {
        return firstUniversityId;
    }

    public void setFirstUniversityId(Integer firstUniversityId) {
        this.firstUniversityId = firstUniversityId;
    }

    public String getFirstUniversityName() {
        return firstUniversityName;
    }

    public void setFirstUniversityName(String firstUniversityName) {
        this.firstUniversityName = firstUniversityName;
    }

    public Integer getFirstSpecialtysId() {
        return firstSpecialtysId;
    }

    public void setFirstSpecialtysId(Integer firstSpecialtysId) {
        this.firstSpecialtysId = firstSpecialtysId;
    }

    public String getFirstSpecialtysName() {
        return firstSpecialtysName;
    }

    public void setFirstSpecialtysName(String firstSpecialtysName) {
        this.firstSpecialtysName = firstSpecialtysName;
    }

    public String getFirstStatus() {
        return firstStatus;
    }

    public void setFirstStatus(String firstStatus) {
        this.firstStatus = firstStatus;
    }

    public Integer getSecondUniversityId() {
        return secondUniversityId;
    }

    public void setSecondUniversityId(Integer secondUniversityId) {
        this.secondUniversityId = secondUniversityId;
    }

    public String getSecondUniversityName() {
        return secondUniversityName;
    }

    public void setSecondUniversityName(String secondUniversityName) {
        this.secondUniversityName = secondUniversityName;
    }

    public Integer getSecondSpecialtysId() {
        return secondSpecialtysId;
    }

    public void setSecondSpecialtysId(Integer secondSpecialtysId) {
        this.secondSpecialtysId = secondSpecialtysId;
    }

    public String getSecondSpecialtysName() {
        return secondSpecialtysName;
    }

    public void setSecondSpecialtysName(String secondSpecialtysName) {
        this.secondSpecialtysName = secondSpecialtysName;
    }

    public String getSecondStatus() {
        return secondStatus;
    }

    public void setSecondStatus(String secondStatus) {
        this.secondStatus = secondStatus;
    }

    public Integer getThirdUniversityId() {
        return thirdUniversityId;
    }

    public void setThirdUniversityId(Integer thirdUniversityId) {
        this.thirdUniversityId = thirdUniversityId;
    }

    public String getThirdUniversityName() {
        return thirdUniversityName;
    }

    public void setThirdUniversityName(String thirdUniversityName) {
        this.thirdUniversityName = thirdUniversityName;
    }

    public Integer getThirdSpecialtysId() {
        return thirdSpecialtysId;
    }

    public void setThirdSpecialtysId(Integer thirdSpecialtysId) {
        this.thirdSpecialtysId = thirdSpecialtysId;
    }

    public String getThirdSpecialtysName() {
        return thirdSpecialtysName;
    }

    public void setThirdSpecialtysName(String thirdSpecialtysName) {
        this.thirdSpecialtysName = thirdSpecialtysName;
    }

    public String getThirdStatus() {
        return thirdStatus;
    }

    public void setThirdStatus(String thirdStatus) {
        this.thirdStatus = thirdStatus;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }

}