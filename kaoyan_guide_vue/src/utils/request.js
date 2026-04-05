import axios from "axios";
import {ElMessage} from "element-plus";
import router from "@/router/index.js";

const request = axios.create({
    baseURL: import.meta.env.VITE_BASE_URL,
    timeout: 30000  // 普通接口超时时间（生成接口走异步，不受此限制）
})

// request 拦截器
request.interceptors.request.use(config => {
    if (config.data instanceof FormData) {
        delete config.headers['Content-Type'];
    } else {
        config.headers['Content-Type'] = 'application/json;charset=utf-8';
    }
    let user = JSON.parse(localStorage.getItem("xm-user") || '{}')
    config.headers['token'] = user.token || ''
    return config
}, error => {
    return Promise.reject(error)
});

// response 拦截器
request.interceptors.response.use(
    response => {
        let res = response.data;
        // 如果是返回的文件
        if (response.config.responseType === 'blob') {
            if (response.config.returnRawResponse) {
                return response
            }
            return res
        }
        // 当权限验证不通过的时候给出提示
        if (res.code === '401') {
            ElMessage.error(res.msg)
            router.push('/login')
        }
        // 兼容服务端返回的字符串数据
        if (typeof res === 'string') {
            res = res ? JSON.parse(res) : res
        }
        return res;
    },
    error => {
        // 区分三类错误：超时 / 服务端异常 / 网络异常
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
            ElMessage.error({ message: '请求超时，请检查网络或稍后重试', duration: 5000 })
        } else if (error.response) {
            const status = error.response.status
            if (status === 404) {
                ElMessage.error('未找到请求接口')
            } else if (status === 500) {
                ElMessage.error('服务端异常，请稍后重试')
            } else if (status === 401) {
                ElMessage.error('登录已过期，请重新登录')
                router.push('/login')
            } else {
                ElMessage.error(`请求失败（${status}），请稍后重试`)
            }
        } else {
            // 无 response：网络中断、CORS、DNS 失败等
            ElMessage.error('网络连接异常，请检查网络后重试')
        }
        return Promise.reject(error)
    }
)

export default request
