import $ from 'jquery'
import { BackendRootURL } from "./config"
import router from '@/router/index'

export const CheckIsLogin = async(store) => {
    return new Promise((resolve) => {
        if(store.state.user.token !== '') {
            $.ajax({
                url: BackendRootURL + '/auth/checktoken',
                type: "POST",
                headers: {
                    'Authorization': "Bearer " + store.state.user.token,
                },
                success: (resp)=> {
                    if (resp.status != 0) {
                        store.commit("logout")
                        router.push({
                            name: "login",
                        })
                        resolve(false)
                    } else {
                        resolve(true)
                    }
                }
            })
        } else {
            store.commit("logout")
            router.push({
                name: "login",
            })
            resolve(false)
        }
    })
}