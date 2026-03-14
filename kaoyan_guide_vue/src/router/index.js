import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    {
      path: '/manager',
      component: () => import('@/views/Manager.vue'),
      children: [
        { path: 'home', meta: { name: '系统首页' }, component: () => import('@/views/manager/Home.vue'),  },
        { path: 'admin', meta: { name: '管理员信息' }, component: () => import('@/views/manager/Admin.vue'), },
        { path: 'user', meta: { name: '学生信息' }, component: () => import('@/views/manager/User.vue'), },
        { path: 'university', meta: { name: '大学信息' }, component: () => import('@/views/manager/University.vue'), },
        { path: 'notice', meta: { name: '系统公告' }, component: () => import('@/views/manager/Notice.vue'), },
        { path: 'person', meta: { name: '个人资料' }, component: () => import('@/views/manager/Person.vue'), },
        { path: 'password', meta: { name: '修改密码' }, component: () => import('@/views/manager/Password.vue'), },
        { path: 'areas', meta: { name: '地区信息' }, component: () => import('@/views/manager/Areas.vue')},
        { path: 'categorys', meta: { name: '门类信息' }, component: () => import('@/views/manager/Categorys.vue')},
        { path: 'specialtys', meta: { name: '专业信息' }, component: () => import('@/views/manager/Specialtys.vue')},
        { path: 'slideshow', meta: { name: '轮播图信息' }, component: () => import('@/views/manager/Slideshow.vue')},
        { path: 'interpretations', meta: { name: '专业解读' }, component: () => import('@/views/manager/Interpretations.vue')},
        { path: 'comment', meta: { name: '学校评价' }, component: () => import('@/views/manager/Comment.vue')},
        { path: 'policys', meta: { name: '招生政策' }, component: () => import('@/views/manager/Policys.vue')},
        { path: 'universitySpecialtys', meta: { name: '学校专业' }, component: () => import('@/views/manager/UniversitySpecialtys.vue')},
        { path: 'dataStatistics', meta: { name: '数据统计' }, component: () => import('@/views/manager/DataStatistics.vue')},
        { path: 'question', meta: { name: '题库管理' }, component: () => import('@/views/manager/Question.vue')},
      ]
    },
    {
      path: '/front',
      component: () => import('@/views/Front.vue'),
      children: [
        { path: 'home', component: () => import('@/views/front/Home.vue'),  },
        { path: 'person', component: () => import('@/views/front/Person.vue'),  },
        { path: 'password', component: () => import('@/views/front/Password.vue'),  },
        { path: 'noticeList', component: () => import('@/views/front/NoticeList.vue'),  },
        { path: 'universityList', component: () => import('@/views/front/UniversityList.vue'),  },
        { path: 'universityDetail', component: () => import('@/views/front/UniversityDetail.vue'),  },
        { path: 'interpretationsList', component: () => import('@/views/front/InterpretationsList.vue'),  },
        { path: 'interpretationsDetail', component: () => import('@/views/front/InterpretationsDetail.vue'),  },
        { path: 'policysList', component: () => import('@/views/front/PolicysList.vue'),  },
        { path: 'policysDetail', component: () => import('@/views/front/PolicysDetail.vue'),  },
        { path: 'specialtysDetail', component: () => import('@/views/front/SpecialtysDetail.vue'),  },
        { path: 'myComment', component: () => import('@/views/front/MyComment.vue'),  },
        { path: 'myCollect', component: () => import('@/views/front/MyCollect.vue'),  },
        { path: 'simulateExam', component: () => import('@/views/front/simulateExam.vue'),  },
        { path: 'consultCollege', component: () => import('@/views/front/consultCollege.vue'),  },
        { path: 'studyPlan', component: () => import('@/views/front/StudyPlan.vue'),  },
      ]
    },
    { path: '/login', component: () => import('@/views/Login.vue') },
    { path: '/register', component: () => import('@/views/Register.vue') },
    { path: '/404', component: () => import('@/views/404.vue') },
    { path: '/:pathMatch(.*)', redirect: '/404' }
  ]
})

// 切换页面跳转到顶部
router.afterEach(() => {
  setTimeout(() => {
    window.scroll({ top: 0, behavior: 'smooth' })
  }, 0)
})

export default router
