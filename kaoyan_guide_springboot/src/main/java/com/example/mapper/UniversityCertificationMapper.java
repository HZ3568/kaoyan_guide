package com.example.mapper;

import com.example.entity.UniversityCertification;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 操作university_certification相关数据接口
*/
public interface UniversityCertificationMapper {

    /**
      * 新增
    */
    int insert(UniversityCertification universityCertification);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(UniversityCertification universityCertification);

    /**
      * 根据ID查询
    */
    UniversityCertification selectById(Integer id);

    /**
      * 查询所有
    */
    List<UniversityCertification> selectAll(UniversityCertification universityCertification);

    @Select("select * from university_certification where university_id = #{universityId}")
    UniversityCertification selectByUniversityId(Integer universityId);
}