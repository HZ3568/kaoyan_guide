package com.example.service;


import com.example.mapper.ReservationMapper;
import com.example.entity.Reservation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class ReservationService {
    @Autowired
    private ReservationMapper reservationMapper;

    // 添加预约信息
    public void insert(Reservation reservation){
        reservationMapper.insert(reservation);
    }

    // 查询预约信息
    public Reservation selectByPhone(String phone){
        return reservationMapper.selectByPhone(phone);
    }
}
