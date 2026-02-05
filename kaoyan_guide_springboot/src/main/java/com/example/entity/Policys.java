package com.example.entity;


/**
 * 招生政策
*/
public class Policys {
    /** 主键ID */
    private Integer id;
    /** 政策标题 */
    private String name;
    /** 大学IDId */
    private Integer universityId;
    /** 政策简介 */
    private String intro;
    /** 政策详情 */
    private String content;
    /** 浏览量 */
    private Integer viewCount;
    /** 创建时间 */
    private String time;
    private String universityName;
    private String universityAvatar;

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

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
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

    public String getIntro() {
        return intro;
    }

    public void setIntro(String intro) {
        this.intro = intro;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public Integer getViewCount() {
        return viewCount;
    }

    public void setViewCount(Integer viewCount) {
        this.viewCount = viewCount;
    }

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }

}