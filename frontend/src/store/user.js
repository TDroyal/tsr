import $ from 'jquery'
import { jwtDecode } from 'jwt-decode'
import {BackendRootURL} from '@/config/config'

const ModuleUser = {
  state: {  // 存全局用户信息
    id: "",
    username: "",
    avatar: BackendRootURL + "/static/avatar.jpg",
    token: "",
    is_login: false,
  },
  getters: {
  },
  mutations: {  // 更新state里面的数据  可以通过$store.commit()触发
    updateUser: (state, user)=> {
        state.id = user.user_id,
        state.username = user.username,
        state.token = user.token,
        state.is_login = user.is_login

        let u = {
            user: state
        }

        localStorage.setItem("userStore", JSON.stringify(u))
    },

    logout: (state)=> {
        state.id = "",
        state.username = "",
        state.token = "",
        state.is_login = false,
        window.localStorage.removeItem("userStore")
    }
  },
  actions: { // 对state的各种操作 支持异步，可以通过$store.dispatch()触发
    login: (context, data)=> {
        let username = data.username
        let password = data.password
        $.ajax({
            url: BackendRootURL + "/auth/login",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({  //  转为JSON字符串
                username: username,
                password: password,
            }),
            success: (resp)=>{
                if (resp.status != 0) {
                    data.error(resp.message)
                    return
                }
                const token = resp.token
                const token_obj = jwtDecode(token)
                console.log(token, token_obj)

                context.commit("updateUser", {  //传入mutations中的方法名称和参数data
                    user_id: token_obj.user_id,
                    username: token_obj.username,
                    token: token,
                    is_login: true,
                })

                // 显示登录成功
                data.success()  //调用login.vue里面的回调函数
            },
            error: (resp)=> {
                data.error(resp.message)
            }
        })
    }
  },
  modules: {
  }
}


export default ModuleUser