package com.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Reservation {
    private Long id;
    private String name;
    private String gender;
    private String phone;
    private LocalDateTime communication_time;
    private String province;
    private Integer estimated_score;
}
