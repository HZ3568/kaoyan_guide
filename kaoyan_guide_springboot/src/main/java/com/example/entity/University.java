package com.example.entity;

import java.math.BigDecimal;

public class University extends Account {

    /** 主键ID */
    private Integer id;
    /** 账号 */
    private String username;
    private String password;
    private String name;
    private String avatar;
    private String role;
    private String phone;
    private String email;
    private String status;
    private Integer areasId;
    private String areasName;
    private String address;
    private String department;
    private String characters;
    private String officialWebsite;
    private String content;
    private BigDecimal mark;
    private String level;
    private Boolean collectFlag;
    private Boolean commentFlag;

    public Boolean getCommentFlag() {
        return commentFlag;
    }

    public void setCommentFlag(Boolean commentFlag) {
        this.commentFlag = commentFlag;
    }

    public Boolean getCollectFlag() {
        return collectFlag;
    }

    public void setCollectFlag(Boolean collectFlag) {
        this.collectFlag = collectFlag;
    }

    public String getCharacters() {
        return characters;
    }

    public void setCharacters(String characters) {
        this.characters = characters;
    }

    public String getLevel() {
        return level;
    }

    public void setLevel(String level) {
        this.level = level;
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

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }



    public String getOfficialWebsite() {
        return officialWebsite;
    }

    public void setOfficialWebsite(String officialWebsite) {
        this.officialWebsite = officialWebsite;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public BigDecimal getMark() {
        return mark;
    }

    public void setMark(BigDecimal mark) {
        this.mark = mark;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
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

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}
