package com.example.entity;


/**
 * 专业解读
*/
public class Interpretations {
    /** 主键ID */
    private Integer id;
    /** 解读标题 */
    private String name;
    /** 门类IDId */
    private Integer categorysId;
    /** 解读简介 */
    private String intro;
    /** 封面图片 */
    private String img;
    /** 解读详情 */
    private String content;
    /** 创建时间 */
    private String time;
    private Integer viewCount;
    private String categorysName;

    public Integer getViewCount() {
        return viewCount;
    }

    public void setViewCount(Integer viewCount) {
        this.viewCount = viewCount;
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

    public String getIntro() {
        return intro;
    }

    public void setIntro(String intro) {
        this.intro = intro;
    }

    public String getImg() {
        return img;
    }

    public void setImg(String img) {
        this.img = img;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }

}