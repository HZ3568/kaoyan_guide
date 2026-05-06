package com.example.entity;

import java.time.LocalDateTime;
import java.math.BigDecimal;

public class University {
    private Integer id;
    private String name;
    private String avatar;
    private Integer provinceId;
    private String provinceName;
    private String address;
    private String schoolType;
    private String educationLevel;
    private Integer is985;
    private Integer is211;
    private Integer isDoubleFirstClass;
    private String officialWebsite;
    private String description;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    private Boolean collectFlag;
    private Boolean commentFlag;
    private BigDecimal longitude; // 百度经度(BD09)
    private BigDecimal latitude;  // 百度纬度(BD09)
    private String englishName;
    private String foundedYear;
    private String affiliation;
    private String leaderInfo;
    private String schoolIntro;
    private String campusEnvironment;
    private String contactAddress;
    private String contactPhone;
    private String contactEmail;
    private String postcode;
    private String libraryInfo;
    private String dormitoryInfo;
    private String canteenInfo;
    private String transportInfo;
    private String masterProgramInfo;
    private String keyDisciplineInfo;
    private String featuredMajorInfo;
    private String firstClassMajorInfo;
    private String graduateHotMajorInfo;

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

    public String getAvatar() {
        return avatar;
    }

    public void setAvatar(String avatar) {
        this.avatar = avatar;
    }

    public Integer getProvinceId() {
        return provinceId;
    }

    public void setProvinceId(Integer provinceId) {
        this.provinceId = provinceId;
    }

    public String getProvinceName() {
        return provinceName;
    }

    public void setProvinceName(String provinceName) {
        this.provinceName = provinceName;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getSchoolType() {
        return schoolType;
    }

    public void setSchoolType(String schoolType) {
        this.schoolType = schoolType;
    }

    public String getEducationLevel() {
        return educationLevel;
    }

    public void setEducationLevel(String educationLevel) {
        this.educationLevel = educationLevel;
    }

    public Integer getIs985() {
        return is985;
    }

    public void setIs985(Integer is985) {
        this.is985 = is985;
    }

    public Integer getIs211() {
        return is211;
    }

    public void setIs211(Integer is211) {
        this.is211 = is211;
    }

    public Integer getIsDoubleFirstClass() {
        return isDoubleFirstClass;
    }

    public void setIsDoubleFirstClass(Integer isDoubleFirstClass) {
        this.isDoubleFirstClass = isDoubleFirstClass;
    }

    public String getOfficialWebsite() {
        return officialWebsite;
    }

    public void setOfficialWebsite(String officialWebsite) {
        this.officialWebsite = officialWebsite;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public LocalDateTime getCreateTime() {
        return createTime;
    }

    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }

    public LocalDateTime getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(LocalDateTime updateTime) {
        this.updateTime = updateTime;
    }

    public Boolean getCollectFlag() {
        return collectFlag;
    }

    public void setCollectFlag(Boolean collectFlag) {
        this.collectFlag = collectFlag;
    }

    public Boolean getCommentFlag() {
        return commentFlag;
    }

    public void setCommentFlag(Boolean commentFlag) {
        this.commentFlag = commentFlag;
    }

    public BigDecimal getLongitude() {
        return longitude;
    }

    public void setLongitude(BigDecimal longitude) {
        this.longitude = longitude;
    }

    public BigDecimal getLatitude() {
        return latitude;
    }

    public void setLatitude(BigDecimal latitude) {
        this.latitude = latitude;
    }

    public String getEnglishName() { return englishName; }
    public void setEnglishName(String englishName) { this.englishName = englishName; }

    public String getFoundedYear() { return foundedYear; }
    public void setFoundedYear(String foundedYear) { this.foundedYear = foundedYear; }

    public String getAffiliation() { return affiliation; }
    public void setAffiliation(String affiliation) { this.affiliation = affiliation; }

    public String getLeaderInfo() { return leaderInfo; }
    public void setLeaderInfo(String leaderInfo) { this.leaderInfo = leaderInfo; }

    public String getSchoolIntro() { return schoolIntro; }
    public void setSchoolIntro(String schoolIntro) { this.schoolIntro = schoolIntro; }

    public String getCampusEnvironment() { return campusEnvironment; }
    public void setCampusEnvironment(String campusEnvironment) { this.campusEnvironment = campusEnvironment; }

    public String getContactAddress() { return contactAddress; }
    public void setContactAddress(String contactAddress) { this.contactAddress = contactAddress; }

    public String getContactPhone() { return contactPhone; }
    public void setContactPhone(String contactPhone) { this.contactPhone = contactPhone; }

    public String getContactEmail() { return contactEmail; }
    public void setContactEmail(String contactEmail) { this.contactEmail = contactEmail; }

    public String getPostcode() { return postcode; }
    public void setPostcode(String postcode) { this.postcode = postcode; }

    public String getLibraryInfo() { return libraryInfo; }
    public void setLibraryInfo(String libraryInfo) { this.libraryInfo = libraryInfo; }

    public String getDormitoryInfo() { return dormitoryInfo; }
    public void setDormitoryInfo(String dormitoryInfo) { this.dormitoryInfo = dormitoryInfo; }

    public String getCanteenInfo() { return canteenInfo; }
    public void setCanteenInfo(String canteenInfo) { this.canteenInfo = canteenInfo; }

    public String getTransportInfo() { return transportInfo; }
    public void setTransportInfo(String transportInfo) { this.transportInfo = transportInfo; }

    public String getMasterProgramInfo() { return masterProgramInfo; }
    public void setMasterProgramInfo(String masterProgramInfo) { this.masterProgramInfo = masterProgramInfo; }

    public String getKeyDisciplineInfo() { return keyDisciplineInfo; }
    public void setKeyDisciplineInfo(String keyDisciplineInfo) { this.keyDisciplineInfo = keyDisciplineInfo; }

    public String getFeaturedMajorInfo() { return featuredMajorInfo; }
    public void setFeaturedMajorInfo(String featuredMajorInfo) { this.featuredMajorInfo = featuredMajorInfo; }

    public String getFirstClassMajorInfo() { return firstClassMajorInfo; }
    public void setFirstClassMajorInfo(String firstClassMajorInfo) { this.firstClassMajorInfo = firstClassMajorInfo; }

    public String getGraduateHotMajorInfo() { return graduateHotMajorInfo; }
    public void setGraduateHotMajorInfo(String graduateHotMajorInfo) { this.graduateHotMajorInfo = graduateHotMajorInfo; }
}
