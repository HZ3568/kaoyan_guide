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

    /**
     * 提供给大模型调用的预约写入工具。
     * 当对话中用户明确给出预约关键信息后，模型可调用该函数落库。
     */
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

    /**
     * 提供给大模型调用的预约查询工具。
     * 用于根据手机号回查用户是否已有预约及预约详情。
     */
    @Tool("根据考生手机号查询预约信息")
    public Reservation queryReservationByPhone(
            @P("考生手机号") String phone) {
        return reservationService.selectByPhone(phone);
    }

}
