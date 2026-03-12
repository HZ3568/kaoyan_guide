package com.example.service.chat;

import com.example.common.enums.ModuleType;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class VolunteerApplyToolProvider implements ModuleToolProvider {
    @Override
    public ModuleType moduleType() {
        return ModuleType.VOLUNTEER_APPLY;
    }

    @Override
    public List<String> toolNames() {
        return List.of("addReservation", "queryReservationByPhone");
    }
}
