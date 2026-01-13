<template>
  <nav class="navbar navbar-expand-lg bg-body-tertiary mynav">
    <div class="container">
      <!-- <a class="navbar-brand" href="#">时序系统</a> -->
      <router-link v-if="$store.state.user.is_login" class="navbar-brand" :to="{name:'home'}">时序系统</router-link>
      <router-link v-else class="navbar-brand" :to="{name:'login'}">时序系统</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarText" aria-controls="navbarText" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarText">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item"  v-if="$store.state.user.is_login">
            <router-link class="nav-link mynav-link" :to="{name:'home'}">首页</router-link>
          </li>
          <li class="nav-item"  v-if="$store.state.user.is_login">
            <router-link class="nav-link mynav-link" :to="{name:'forcast'}" v-if="$store.state.user.is_login">预测任务</router-link>
          </li>
          <li class="nav-item"  v-if="$store.state.user.is_login">
            <router-link class="nav-link mynav-link" :to="{name:'anomalydetection'}" v-if="$store.state.user.is_login">异常检测任务</router-link>
          </li>
          <li class="nav-item"  v-if="$store.state.user.is_login">
            <router-link class="nav-link mynav-link" :to="{name:'chat'}" v-if="$store.state.user.is_login">智能时序问答助手</router-link>
          </li>
        </ul>
        <ul class="navbar-nav" v-if="!$store.state.user.is_login">
          <li class="nav-item">
            <router-link class="nav-link mynav-link" :to="{name:'login'}">登录</router-link>
          </li>
        </ul>
        <!-- 登录成功显示头像和名称 + 退出登录 -->
        <ul class="navbar-nav" v-else>
          <div class="nav-item dropdown">
            <a class="nav-item dropdown-toggle mynav-link" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                <img class="img-fluid avatar" :src="$store.state.user.avatar" alt="">
                {{$store.state.user.username}}
            </a>

            <ul class="dropdown-menu">
                <li>
                    <router-link class="my-dropdown-item dropdown-item " :to="{name:'login'}" @click="logout">
                        <svg t="1713430848986" class="icon mysvg" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5778" width="200" height="200"><path d="M184.552727 768l0-512c0-38.539636 31.278545-69.818182 69.818182-69.818182l302.545455 0L556.916364 139.636364l-325.818182 0c-51.432727 0-93.090909 41.658182-93.090909 93.090909l0 558.545455c0 51.432727 41.658182 93.090909 93.090909 93.090909l325.818182 0 0-46.545455-302.545455 0C215.784727 837.818182 184.552727 806.539636 184.552727 768zM924.113455 495.522909l-164.584727-164.584727c-9.076364-9.076364-23.831273-9.076364-32.907636 0-9.076364 9.076364-9.076364 23.831273 0 32.907636l124.834909 124.834909L394.007273 488.680727c-12.846545 0-23.272727 10.426182-23.272727 23.272727s10.426182 23.272727 23.272727 23.272727l457.448727 0-124.834909 124.834909c-9.076364 9.076364-9.076364 23.831273 0 32.907636 9.076364 9.076364 23.831273 9.076364 32.907636 0l164.584727-164.584727C933.189818 519.354182 933.189818 504.645818 924.113455 495.522909z" fill="#2c2c2c" p-id="5779"></path></svg>
                        <span style="padding-left: 5px;">退出</span>
                    </router-link>
                </li>
            </ul>
          </div>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import {useStore} from 'vuex'
export default {
  name: 'NavbarComponent',
  components: {
    
  },
  setup: ()=> {
    const store = useStore()
    const logout = ()=> {
      store.commit('logout')
    }
    return {
      logout,
      store,
    }
  }
}
</script>

<style scoped>
a{
    text-decoration: none; /* 取消下划线 */
    color: black; /* 修改字体颜色，这里以红色为例 */
}

.mynav{
    background-color: white;
    /* background-color: #F7F7F7; */
    position: fixed;
    top: 0;
    width: 100vw;
    z-index: 1000;
}

.mynav-link{
    color: rgb(107, 107, 107);
}

.mynav-link:hover{
    color: black;
}

.mynav-link:hover .original-icon {
    display: none;
}

.mynav-link:hover .hover-icon {
    display: block;
}

.avatar{
    width: 30px; 
    height: 30px; 
    border-radius: 50%;
}

.my-dropdown-item{
    display: flex; 
    align-items: center;
}

.mysvg{
    max-height: 25px;
    max-width: 25px;
}
</style>