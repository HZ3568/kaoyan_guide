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
    /** 专业简介 */
    private String intro;
    /** 培养目标 */
    private String trainingObjective;
    /** 主要课程 */
    private String mainCourses;
    /** 就业方向 */
    private String employmentDirection;
    /** 官方来源 */
    private String officialSourceUrl;

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

    public String getIntro() {
        return intro;
    }

    public void setIntro(String intro) {
        this.intro = intro;
    }

    public String getTrainingObjective() {
        return trainingObjective;
    }

    public void setTrainingObjective(String trainingObjective) {
        this.trainingObjective = trainingObjective;
    }

    public String getMainCourses() {
        return mainCourses;
    }

    public void setMainCourses(String mainCourses) {
        this.mainCourses = mainCourses;
    }

    public String getEmploymentDirection() {
        return employmentDirection;
    }

    public void setEmploymentDirection(String employmentDirection) {
        this.employmentDirection = employmentDirection;
    }

    public String getOfficialSourceUrl() {
        return officialSourceUrl;
    }

    public void setOfficialSourceUrl(String officialSourceUrl) {
        this.officialSourceUrl = officialSourceUrl;
    }

}