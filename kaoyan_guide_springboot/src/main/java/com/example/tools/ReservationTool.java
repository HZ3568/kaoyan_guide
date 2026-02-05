package com.example.tools;

import com.example.entity.Reservation;
import com.example.service.ReservationService;
import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class ReservationTool {
    @Autowired
    private ReservationService reservationService;


    // 1. 添加预约信息
    @Tool("预约志愿填报服务")
    public void addReservation(
            @P("考生姓名") String name,
            @P("考生性别") String gender,
            @P("考生电话") String phone,
            @P("沟通时间") LocalDateTime communication_time,
            @P("考生所在省份") String province,
            @P("考生预估分数") Integer estimated_score) {
        Reservation reservation = new Reservation(null, name, gender, phone, communication_time, province, estimated_score);
        reservationService.insert(reservation);
    }

    // 2. 查询预约信息
    @Tool("根据考生手机号查询预约信息")
    public Reservation queryReservationByPhone(
            @P("考生手机号") String phone) {
        return reservationService.selectByPhone(phone);
    }

}
