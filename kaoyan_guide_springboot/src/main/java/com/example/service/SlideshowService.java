package com.example.service;

import com.example.entity.Slideshow;
import com.example.mapper.SlideshowMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import java.util.List;

/**
 * 轮播图信息业务处理
 **/
@Service
public class SlideshowService {

    @Resource
    private SlideshowMapper slideshowMapper;

    /**
     * 新增
     */
    public void add(Slideshow slideshow) {
        slideshowMapper.insert(slideshow);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        slideshowMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            slideshowMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Slideshow slideshow) {
        slideshowMapper.updateById(slideshow);
    }

    /**
     * 根据ID查询
     */
    public Slideshow selectById(Integer id) {
        return slideshowMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<Slideshow> selectAll(Slideshow slideshow) {
        return slideshowMapper.selectAll(slideshow);
    }

    /**
     * 分页查询
     */
    public PageInfo<Slideshow> selectPage(Slideshow slideshow, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Slideshow> list = this.selectAll(slideshow);
        return PageInfo.of(list);
    }

}