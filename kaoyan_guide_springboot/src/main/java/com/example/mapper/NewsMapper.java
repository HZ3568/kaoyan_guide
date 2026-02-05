package com.example.mapper;

import com.example.entity.News;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 操作news相关数据接口
*/
public interface NewsMapper {

    /**
      * 新增
    */
    int insert(News news);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(News news);

    /**
      * 根据ID查询
    */
    News selectById(Integer id);

    /**
      * 查询所有
    */
    List<News> selectAll(News news);

    @Select("select * from news order by view_count desc limit 0, 6")
    List<News> loadHotNews();
}