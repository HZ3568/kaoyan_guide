package com.example.mapper;

import com.example.entity.Slideshow;
import java.util.List;

/**
 * 操作slideshow相关数据接口
*/
public interface SlideshowMapper {

    /**
      * 新增
    */
    int insert(Slideshow slideshow);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(Slideshow slideshow);

    /**
      * 根据ID查询
    */
    Slideshow selectById(Integer id);

    /**
      * 查询所有
    */
    List<Slideshow> selectAll(Slideshow slideshow);

}