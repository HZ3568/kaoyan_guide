package com.example.mapper;

import com.example.entity.Specialtys;
import java.util.List;

/**
 * 操作specialtys相关数据接口
*/
public interface SpecialtysMapper {

    /**
      * 新增
    */
    int insert(Specialtys specialtys);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(Specialtys specialtys);

    /**
      * 根据ID查询
    */
    Specialtys selectById(Integer id);

    /**
      * 查询所有
    */
    List<Specialtys> selectAll(Specialtys specialtys);

}