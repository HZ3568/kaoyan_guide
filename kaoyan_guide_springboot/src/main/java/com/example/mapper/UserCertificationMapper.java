package com.example.mapper;

import com.example.entity.UserCertification;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 操作user_certification相关数据接口
*/
public interface UserCertificationMapper {

    /**
      * 新增
    */
    int insert(UserCertification userCertification);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(UserCertification userCertification);

    /**
      * 根据ID查询
    */
    UserCertification selectById(Integer id);

    /**
      * 查询所有
    */
    List<UserCertification> selectAll(UserCertification userCertification);

    @Select("select * from user_certification where user_id = #{userId}")
    UserCertification selectByUserId(Integer userId);
}