package com.example.mapper;

import com.example.entity.Comment;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 操作comment相关数据接口
*/
public interface CommentMapper {

    /**
      * 新增
    */
    int insert(Comment comment);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(Comment comment);

    /**
      * 根据ID查询
    */
    Comment selectById(Integer id);

    /**
      * 查询所有
    */
    List<Comment> selectAll(Comment comment);

    @Select("select * from comment where user_id = #{userId} and university_id = #{universityId}")
    Comment selectByUserIdAndUniversityId(Integer userId, Integer universityId);

    @Select("select * from comment where university_id = #{universityId}")
    List<Comment> selectByUniversityId(Integer universityId);
}