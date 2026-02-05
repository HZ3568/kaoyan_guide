package com.example.mapper;

import com.example.entity.Policys;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 操作policys相关数据接口
*/
public interface PolicysMapper {

    /**
      * 新增
    */
    int insert(Policys policys);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(Policys policys);

    /**
      * 根据ID查询
    */
    Policys selectById(Integer id);

    /**
      * 查询所有
    */
    List<Policys> selectAll(Policys policys);

    @Select("select * from policys order by view_count desc limit 0, 10")
    List<Policys> loadHotPolicys();
}