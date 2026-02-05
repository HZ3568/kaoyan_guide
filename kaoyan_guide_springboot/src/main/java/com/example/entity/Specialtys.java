package com.example.entity;


/**
 * 专业信息
*/
public class Specialtys {
    /** 主键ID */
    private Integer id;
    /** 门类IDId */
    private Integer categorysId;
    /** 专业名称 */
    private String name;
    /** 专业代码 */
    private String specialtyNumber;
    private String categorysName;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
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

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getSpecialtyNumber() {
        return specialtyNumber;
    }

    public void setSpecialtyNumber(String specialtyNumber) {
        this.specialtyNumber = specialtyNumber;
    }

}