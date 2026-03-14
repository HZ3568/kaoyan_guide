package com.example.service;

import com.example.entity.DailyQuestion;
import com.example.entity.Question;
import com.example.mapper.DailyQuestionMapper;
import com.example.mapper.QuestionMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Service
public class QuestionService {

    @Resource
    private QuestionMapper questionMapper;

    @Resource
    private DailyQuestionMapper dailyQuestionMapper;

    public void add(Question question) {
        prepareQuestion(question);
        question.setCreateTime(LocalDateTime.now());
        question.setUpdateTime(LocalDateTime.now());
        questionMapper.insert(question);
    }

    public void updateById(Question question) {
        prepareQuestion(question);
        question.setUpdateTime(LocalDateTime.now());
        questionMapper.updateById(question);
    }

    public void deleteById(Long id) {
        questionMapper.deleteById(id);
    }

    public void deleteBatch(List<Long> ids) {
        for (Long id : ids) {
            questionMapper.deleteById(id);
        }
    }

    public Question selectById(Long id) {
        return questionMapper.selectById(id);
    }

    public List<Question> selectAll(Question question) {
        return questionMapper.selectAll(question);
    }

    public PageInfo<Question> selectPage(Question question, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Question> list = questionMapper.selectAll(question);
        return PageInfo.of(list);
    }

    @Transactional(rollbackFor = Exception.class)
    public void assignDailyQuestion(LocalDate questionDate, Long questionId) {
        Question question = questionMapper.selectById(questionId);
        if (question == null) {
            throw new RuntimeException("题目不存在");
        }
        DailyQuestion existed = dailyQuestionMapper.selectByDate(questionDate);
        if (existed == null) {
            DailyQuestion dailyQuestion = new DailyQuestion();
            dailyQuestion.setQuestionDate(questionDate);
            dailyQuestion.setQuestionId(questionId);
            dailyQuestion.setCreateTime(LocalDateTime.now());
            dailyQuestionMapper.insert(dailyQuestion);
            return;
        }
        DailyQuestion dailyQuestion = new DailyQuestion();
        dailyQuestion.setQuestionDate(questionDate);
        dailyQuestion.setQuestionId(questionId);
        dailyQuestionMapper.updateByDate(dailyQuestion);
    }

    public List<Map<String, Object>> selectRecentAssignments(LocalDate startDate, LocalDate endDate) {
        return dailyQuestionMapper.selectRecentAssignments(startDate, endDate);
    }

    private void prepareQuestion(Question question) {
        if (question.getDifficulty() == null || question.getDifficulty().trim().isEmpty()) {
            question.setDifficulty("medium");
        }
        if (question.getStatus() == null) {
            question.setStatus(1);
        }
    }
}
