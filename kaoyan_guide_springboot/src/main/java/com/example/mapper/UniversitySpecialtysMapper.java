package com.example.mapper;

import com.example.entity.UniversitySpecialtys;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 操作university_specialtys相关数据接口
*/
public interface UniversitySpecialtysMapper {

    /**
      * 新增
    */
    int insert(UniversitySpecialtys universitySpecialtys);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(UniversitySpecialtys universitySpecialtys);

    /**
      * 根据ID查询
    */
    UniversitySpecialtys selectById(Integer id);

    /**
      * 查询所有
    */
    List<UniversitySpecialtys> selectAll(UniversitySpecialtys universitySpecialtys);

    @Select("select * from university_specialtys where university_id = #{universityId} and categorys_id = #{categorysId} and specialtys_id = #{specialtysId}")
    UniversitySpecialtys selectByUniversityIdCategorysIdAndSpecialtysId(Integer universityId, Integer categorysId, Integer specialtysId);
}