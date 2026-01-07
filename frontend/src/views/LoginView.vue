<template>
  <ContentComponent>
    <div class="row justify-content-center">
        <div class="col-12 col-md-5">
            <div class="card">
            <div class="card-body">
                <!-- 登录界面 -->
                <form @submit.prevent="login">
                    <div class="mb-3">
                        <input v-model="username" type="text" class="form-control" id="username" placeholder="用户名" autocomplete="username" required>
                    </div>
                
                    <div class="mb-3">
                        <input v-model="password" type="password" class="form-control" id="password" placeholder="密码" autocomplete="current-password" required>
                    </div>
                    
                    <div class="mb-3">
                        <div class="row" style="display: flex; justify-content: center;">
                            <div class="error-message">{{ error_message }}</div>
                        </div>
                    </div>

                    <div class="d-flex justify-content-center">
                        <button type="submit" class="btn btn-primary position-relative">登录</button>
                    </div>
                </form>

            </div>
            </div>
        </div>
    </div>
  </ContentComponent>
</template>

<script>
import ContentComponent from '@/components/ContentComponent.vue'
import {useStore} from 'vuex'
import router from '@/router/index'
import {ref} from 'vue'

export default {
  name: 'LoginView',
  components: {
    ContentComponent,
  },
  setup() {
    const store = useStore()
    let username = ref('')
    let password = ref('')
    let error_message = ref('')

    const login = ()=> {
        error_message.value = ""
        store.dispatch("login", {
            username: username.value,
            password: password.value,
            success() {
                // 可以添加一个登录成功的提示
                router.push({name: "home"})
            },
            error: (msg)=> {
                error_message.value = msg
            }
        })
    }

    return {
        username,
        password,
        error_message,
        login,
    }

  }
}
</script>

<style scoped>
button{
    width: 80%;
    margin: auto;
}

input {
    width: 80%;
    margin: auto;
}

.error-message {
    color: red;
    /* margin-top: 0px; */
    width: 80%;
    margin: auto;
    margin-top: 5px;
}
</style>

