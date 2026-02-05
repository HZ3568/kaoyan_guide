package com.example.entity;


/**
 * 轮播图信息
*/
public class Slideshow {
    /** 主键ID */
    private Integer id;
    /** 大学IDId */
    private Integer universityId;
    /** 轮播图图片 */
    private String img;
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

    public String getImg() {
        return img;
    }

    public void setImg(String img) {
        this.img = img;
    }

}