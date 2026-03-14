package com.example.mapper;

import com.example.entity.University;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface UniversityMapper {

    int insert(University university);

    void updateById(University university);

    void deleteById(Integer id);

    @Select("select u.*, p.name as provinceName from university u " +
            "left join areas p on p.id = u.province_id where u.id = #{id}")
    University selectById(Integer id);

    List<University> selectAll(University university);

    List<University> selectByNames(List<String> names);

    @Select("select u.*, p.name as provinceName from university u " +
            "left join areas p on p.id = u.province_id " +
            "order by u.id desc limit 0, 6")
    List<University> loadHotUniversity();
}
