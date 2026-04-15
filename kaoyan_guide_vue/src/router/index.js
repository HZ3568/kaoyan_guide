import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },

    // ===================== 登录/注册 =====================
    { path: '/login', component: () => import('@/views/Login.vue') },
    { path: '/register', component: () => import('@/views/Register.vue') },
    { path: '/404', component: () => import('@/views/404.vue') },

    // ===================== 管理后台（5大模块） =====================
    {
      path: '/manager',
      component: () => import('@/views/Manager.vue'),
      children: [

        // ---------- 首页 ----------
        { path: 'home', meta: { name: '系统首页' }, component: () => import('@/views/manager/Home.vue') },
        { path: 'person', meta: { name: '个人资料' }, component: () => import('@/views/manager/Person.vue') },
        { path: 'password', meta: { name: '修改密码' }, component: () => import('@/views/manager/Password.vue') },
        { path: 'dataStatistics', meta: { name: '数据统计' }, component: () => import('@/views/manager/DataStatistics.vue') },

        // ---------- 院校信息管理（school） ----------
        {
          path: 'school/university', meta: { name: '学校信息' }, component: () => import('@/views/manager/University.vue'),
        },
        { path: 'school/areas', meta: { name: '地区信息' }, component: () => import('@/views/manager/Areas.vue') },
        { path: 'school/categorys', meta: { name: '门类信息' }, component: () => import('@/views/manager/Categorys.vue') },
        { path: 'school/specialtys', meta: { name: '专业信息' }, component: () => import('@/views/manager/Specialtys.vue') },
        { path: 'school/interpretations', meta: { name: '专业解读' }, component: () => import('@/views/manager/Interpretations.vue') },
        { path: 'school/policys', meta: { name: '招生政策' }, component: () => import('@/views/manager/Policys.vue') },
        { path: 'school/comment', meta: { name: '院校评价' }, component: () => import('@/views/manager/Comment.vue') },
        { path: 'school/universitySpecialtys', meta: { name: '学校专业' }, component: () => import('@/views/manager/UniversitySpecialtys.vue') },

        // ---------- 智能服务管理（ai） ----------
        { path: 'ai/knowledgeBase', meta: { name: '知识库管理' }, component: () => import('@/views/manager/KnowledgeBase.vue') },
        { path: 'ai/consultSession', meta: { name: '咨询会话管理' }, component: () => import('@/views/manager/ConsultSession.vue') },
        { path: 'ai/studyPlan', meta: { name: '学习规划管理' }, component: () => import('@/views/manager/StudyPlanManagement.vue') },

        // ---------- 考试练习管理模块（exam） ----------
        { path: 'exam/question', meta: { name: '每日一题管理' }, component: () => import('@/views/manager/Question.vue') },
        { path: 'exam/examData', meta: { name: '模拟考试数据管理' }, component: () => import('@/views/manager/ExamData.vue') },

        // ---------- 用户管理（user） ----------
        { path: 'user/admin', meta: { name: '管理员信息' }, component: () => import('@/views/manager/Admin.vue') },
        { path: 'user/user', meta: { name: '学生信息' }, component: () => import('@/views/manager/User.vue') },

        // ---------- 系统内容管理（system） ----------
        { path: 'system/slideshow', meta: { name: '轮播图管理' }, component: () => import('@/views/manager/Slideshow.vue') },
        { path: 'system/notice', meta: { name: '系统公告' }, component: () => import('@/views/manager/Notice.vue') },

        // ==================== 旧路径兼容重定向（可逐步废弃） ====================
        { path: 'admin', redirect: '/manager/user/admin' },
        { path: 'user', redirect: '/manager/user/user' },
        { path: 'university', redirect: '/manager/school/university' },
        { path: 'notice', redirect: '/manager/system/notice' },
        { path: 'areas', redirect: '/manager/school/areas' },
        { path: 'categorys', redirect: '/manager/school/categorys' },
        { path: 'specialtys', redirect: '/manager/school/specialtys' },
        { path: 'slideshow', redirect: '/manager/system/slideshow' },
        { path: 'interpretations', redirect: '/manager/school/interpretations' },
        { path: 'comment', redirect: '/manager/school/comment' },
        { path: 'policys', redirect: '/manager/school/policys' },
        { path: 'universitySpecialtys', redirect: '/manager/school/universitySpecialtys' },
        { path: 'question', redirect: '/manager/exam/question' },
        { path: 'knowledgeBase', redirect: '/manager/ai/knowledgeBase' },
      ]
    },

    // ===================== 前台用户端 =====================
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
        { path: 'simulateExamHistory', component: () => import('@/views/front/simulateExamHistory.vue'),  },
        { path: 'consultCollege', component: () => import('@/views/front/consultCollege.vue'),  },
        { path: 'studyPlan', component: () => import('@/views/front/StudyPlan.vue'),  },
      ]
    },

    { path: '/:pathMatch(.*)', redirect: '/404' }
  ]
})

// ==================== 路由守卫 ====================
router.beforeEach((to, from) => {
  const path = to.path;

  // 访问管理后台 → 必须有 admin token 且 role=ADMIN
  if (path.startsWith('/manager')) {
    const admin = JSON.parse(localStorage.getItem('xm-admin') || '{}');
    if (!admin.id) {
      return '/login';
    }
    if (admin.role !== 'ADMIN') {
      // 非管理员强制跳转用户端
      return '/front/home';
    }
  }

  // 访问用户前端 → 必须有 user token 且 role=USER
  if (path.startsWith('/front')) {
    const user = JSON.parse(localStorage.getItem('xm-user') || '{}');
    if (!user.id) {
      return '/login';
    }
    if (user.role !== 'USER') {
      // 管理员走管理端入口
      return '/manager/home';
    }
  }

  // 放行：login / register / 404
  return true;
});

// 切换页面跳转到顶部
router.afterEach(() => {
  setTimeout(() => {
    window.scroll({ top: 0, behavior: 'smooth' })
  }, 0)
})

export default router
