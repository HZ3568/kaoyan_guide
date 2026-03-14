package com.example.tools;

import com.example.entity.University;
import com.example.service.UniversityService;
import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;

@Component
public class SchoolCompareTool {
    @Autowired
    private UniversityService universityService;

    @Tool("当用户要求比较两所或多所学校时，查询这些院校的基础信息用于对比")
    public List<University> compareSchools(
            @P("学校名称列表，多个学校名称用逗号分隔") String schoolNames) {
        if (schoolNames == null) {
            return List.of();
        }
        List<String> names = Arrays.stream(schoolNames.split("[,，]"))
                .map(String::trim)
                .filter(name -> !name.isEmpty())
                .distinct()
                .limit(5)
                .toList();
        if (names.size() < 2) {
            return List.of();
        }
        return universityService.selectByNames(names);
    }
}
