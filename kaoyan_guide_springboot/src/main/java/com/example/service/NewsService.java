package com.example.service;

import cn.hutool.core.date.DateUtil;
import com.example.entity.News;
import com.example.mapper.NewsMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import java.util.List;

/**
 * 高考资讯业务处理
 **/
@Service
public class NewsService {

    @Resource
    private NewsMapper newsMapper;

    /**
     * 新增
     */
    public void add(News news) {
        news.setTime(DateUtil.now());
        news.setViewCount(0);
        newsMapper.insert(news);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        newsMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            newsMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(News news) {
        newsMapper.updateById(news);
    }

    /**
     * 根据ID查询
     */
    public News selectById(Integer id) {
        return newsMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<News> selectAll(News news) {
        return newsMapper.selectAll(news);
    }

    /**
     * 分页查询
     */
    public PageInfo<News> selectPage(News news, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<News> list = this.selectAll(news);
        return PageInfo.of(list);
    }

    public void loadUpdateViewCount(Integer id) {
        News news = newsMapper.selectById(id);
        news.setViewCount(news.getViewCount() + 1);
        newsMapper.updateById(news);
    }

    public List<News> loadHotNews() {
        return newsMapper.loadHotNews();
    }
}