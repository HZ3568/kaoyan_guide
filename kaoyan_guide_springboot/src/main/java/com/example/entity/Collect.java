package com.example.entity;


/**
 * 收藏信息
*/
public class Collect {
    /** 主键ID */
    private Integer id;
    /** 大学IDId */
    private Integer universityId;
    /** 学生IDId */
    private Integer userId;
    private String universityName;
    private String universityAvatar;
    private String userName;

    public String getUniversityAvatar() {
        return universityAvatar;
    }

    public void setUniversityAvatar(String universityAvatar) {
        this.universityAvatar = universityAvatar;
    }

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

}