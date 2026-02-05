package com.example.entity;


/**
 * 学校专业
*/
public class UniversitySpecialtys {
    /** 主键ID */
    private Integer id;
    /** 学校ID */
    private Integer universityId;
    /** 门类ID */
    private Integer categorysId;
    /** 专业ID */
    private Integer specialtysId;
    /** 专业介绍 */
    private String content;
    private String universityName;
    private String categorysName;
    private String specialtysName;

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

    public Integer getCategorysId() {
        return categorysId;
    }

    public void setCategorysId(Integer categorysId) {
        this.categorysId = categorysId;
    }

    public String getCategorysName() {
        return categorysName;
    }

    public void setCategorysName(String categorysName) {
        this.categorysName = categorysName;
    }

    public Integer getSpecialtysId() {
        return specialtysId;
    }

    public void setSpecialtysId(Integer specialtysId) {
        this.specialtysId = specialtysId;
    }

    public String getSpecialtysName() {
        return specialtysName;
    }

    public void setSpecialtysName(String specialtysName) {
        this.specialtysName = specialtysName;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

}