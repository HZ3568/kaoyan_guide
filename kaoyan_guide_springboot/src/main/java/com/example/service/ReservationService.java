package com.example.service;


import com.example.mapper.ReservationMapper;
import com.example.entity.Reservation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class ReservationService {
    @Autowired
    private ReservationMapper reservationMapper;

    /**
     * 新增院校咨询预约记录。
     */
    public void insert(Reservation reservation){
        reservationMapper.insert(reservation);
    }

    /**
     * 按手机号查询预约记录。
     */
    public Reservation selectByPhone(String phone){
        return reservationMapper.selectByPhone(phone);
    }
}
