package com.example.mapper;


import com.example.entity.Reservation;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface ReservationMapper {
    // 1. 添加预约信息
    @Insert("INSERT INTO reservation (name, gender, phone, communication_time, province, estimated_score) VALUES (#{name}, #{gender}, #{phone}, #{communication_time}, #{province}, #{estimated_score})")
    void insert(Reservation reservation);

    // 2. 查询预约信息
    @Select("select * from reservation where phone = #{phone}")
    Reservation selectByPhone(String phone);
}
