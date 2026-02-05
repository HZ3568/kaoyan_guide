package com.example.mapper;

import com.example.entity.Areas;
import java.util.List;

/**
 * 操作areas相关数据接口
*/
public interface AreasMapper {

    /**
      * 新增
    */
    int insert(Areas areas);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(Areas areas);

    /**
      * 根据ID查询
    */
    Areas selectById(Integer id);

    /**
      * 查询所有
    */
    List<Areas> selectAll(Areas areas);

}