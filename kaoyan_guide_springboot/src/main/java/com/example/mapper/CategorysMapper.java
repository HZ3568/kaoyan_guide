package com.example.mapper;

import com.example.entity.Categorys;
import java.util.List;

/**
 * 操作categorys相关数据接口
*/
public interface CategorysMapper {

    /**
      * 新增
    */
    int insert(Categorys categorys);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(Categorys categorys);

    /**
      * 根据ID查询
    */
    Categorys selectById(Integer id);

    /**
      * 查询所有
    */
    List<Categorys> selectAll(Categorys categorys);

}