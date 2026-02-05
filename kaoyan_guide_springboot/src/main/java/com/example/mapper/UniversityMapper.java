package com.example.mapper;

import com.example.entity.Admin;
import com.example.entity.University;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface UniversityMapper {

    int insert(University university);

    void updateById(University university);

    void deleteById(Integer id);

    @Select("select * from `university` where id = #{id}")
    University selectById(Integer id);

    @Select("select * from `university` where username = #{username}")
    University selectByUsername(String username);

    List<University> selectAll(University university);

    @Select("select university.*, areas.name as areasName from university left join areas on areas.id = university.areas_id where status = '审核通过' order by mark desc limit 0, 6")
    List<University> loadHotUniversity();
}
