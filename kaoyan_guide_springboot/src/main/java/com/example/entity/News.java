package com.example.entity;


/**
 * 高考资讯
*/
public class News {
    /** 主键ID */
    private Integer id;
    /** 资讯标题 */
    private String name;
    /** 封面图片 */
    private String img;
    /** 资讯简介 */
    private String intro;
    /** 资讯详情 */
    private String content;
    /** 浏览量 */
    private Integer viewCount;
    /** 创建时间 */
    private String time;

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

    public String getImg() {
        return img;
    }

    public void setImg(String img) {
        this.img = img;
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