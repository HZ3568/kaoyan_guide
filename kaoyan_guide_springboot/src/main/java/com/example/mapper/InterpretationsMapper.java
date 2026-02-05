package com.example.mapper;

import com.example.entity.Interpretations;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 操作interpretations相关数据接口
*/
public interface InterpretationsMapper {

    /**
      * 新增
    */
    int insert(Interpretations interpretations);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(Interpretations interpretations);

    /**
      * 根据ID查询
    */
    Interpretations selectById(Integer id);

    /**
      * 查询所有
    */
    List<Interpretations> selectAll(Interpretations interpretations);

    @Select("select * from interpretations order by view_count desc limit 0, 6")
    List<Interpretations> loadHotInterpretations();
}