package com.example.service;

import com.example.entity.DailyQuestion;
import com.example.entity.Question;
import com.example.entity.QuestionRecord;
import com.example.mapper.DailyQuestionMapper;
import com.example.mapper.QuestionMapper;
import com.example.mapper.QuestionRecordMapper;
import jakarta.annotation.Resource;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
public class DailyQuestionService {

    @Resource
    private QuestionMapper questionMapper;

    @Resource
    private QuestionRecordMapper questionRecordMapper;

    @Resource
    private DailyQuestionMapper dailyQuestionMapper;

    @Transactional(rollbackFor = Exception.class)
    public Question resolveTodayQuestion(LocalDate today) {
        DailyQuestion dailyQuestion = dailyQuestionMapper.selectByDate(today);
        if (dailyQuestion != null) {
            Question assignedQuestion = questionMapper.selectById(dailyQuestion.getQuestionId());
            if (assignedQuestion != null && assignedQuestion.getStatus() != null && assignedQuestion.getStatus() == 1) {
                return assignedQuestion;
            }
        }
        Question question = questionMapper.selectRandomEnabled();
        if (question == null) {
            return null;
        }
        DailyQuestion insertData = new DailyQuestion();
        insertData.setQuestionDate(today);
        insertData.setQuestionId(question.getId());
        insertData.setCreateTime(LocalDateTime.now());
        try {
            dailyQuestionMapper.insert(insertData);
        } catch (DuplicateKeyException ignored) {
        }
        DailyQuestion latest = dailyQuestionMapper.selectByDate(today);
        if (latest != null) {
            return questionMapper.selectById(latest.getQuestionId());
        }
        return question;
    }

    public QuestionRecord getUserRecord(Long userId, LocalDate today) {
        return questionRecordMapper.selectByUserAndDate(userId, today);
    }

    @Transactional(rollbackFor = Exception.class)
    public Map<String, Object> submit(Long userId, String userAnswer) {
        LocalDate today = LocalDate.now();
        QuestionRecord existed = questionRecordMapper.selectByUserAndDate(userId, today);
        if (existed != null) {
            throw new RuntimeException("今日已完成作答");
        }
        Question question = resolveTodayQuestion(today);
        if (question == null) {
            throw new RuntimeException("暂无可用题目");
        }
        String normalizedUserAnswer = normalizeAnswer(userAnswer);
        boolean correct = isAnswerCorrect(question, normalizedUserAnswer);

        QuestionRecord record = new QuestionRecord();
        record.setUserId(userId);
        record.setQuestionId(question.getId());
        record.setUserAnswer(userAnswer);
        record.setIsCorrect(correct ? 1 : 0);
        record.setQuestionDate(today);
        record.setAnswerTime(LocalDateTime.now());
        questionRecordMapper.insert(record);

        return buildAnswerResult(question, userAnswer, correct);
    }

    public Map<String, Object> buildQuestionView(Question question) {
        Map<String, Object> view = new HashMap<>();
        view.put("id", question.getId());
        view.put("subject", question.getSubject());
        view.put("type", question.getType());
        view.put("difficulty", question.getDifficulty());
        view.put("title", question.getTitle());
        view.put("optionA", question.getOptionA());
        view.put("optionB", question.getOptionB());
        view.put("optionC", question.getOptionC());
        view.put("optionD", question.getOptionD());
        return view;
    }

    public Map<String, Object> buildAnswerResult(Question question, String userAnswer, boolean isCorrect) {
        Map<String, Object> result = new HashMap<>();
        result.put("isCorrect", isCorrect);
        result.put("userAnswer", userAnswer);
        result.put("correctAnswer", question.getCorrectAnswer());
        result.put("analysis", question.getAnalysis());
        return result;
    }

    private String normalizeAnswer(String answer) {
        return answer == null ? "" : answer.trim();
    }

    private boolean isAnswerCorrect(Question question, String normalizedUserAnswer) {
        String normalizedCorrectAnswer = normalizeAnswer(question.getCorrectAnswer());
        if (normalizedCorrectAnswer.equalsIgnoreCase(normalizedUserAnswer)) {
            return true;
        }
        String mappedOptionContent = getOptionContentByCode(question, normalizedUserAnswer);
        return mappedOptionContent != null && normalizedCorrectAnswer.equalsIgnoreCase(mappedOptionContent);
    }

    private String getOptionContentByCode(Question question, String code) {
        if ("A".equalsIgnoreCase(code)) {
            return normalizeAnswer(question.getOptionA());
        }
        if ("B".equalsIgnoreCase(code)) {
            return normalizeAnswer(question.getOptionB());
        }
        if ("C".equalsIgnoreCase(code)) {
            return normalizeAnswer(question.getOptionC());
        }
        if ("D".equalsIgnoreCase(code)) {
            return normalizeAnswer(question.getOptionD());
        }
        return null;
    }
}
