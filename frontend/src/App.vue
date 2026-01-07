<template>
  <NavbarComponent />
  <router-view/>
</template>

<script>
import NavbarComponent from './components/NavbarComponent.vue'
import {useStore} from 'vuex'
import {CheckIsLogin} from '@/config/util'
export default{
  components:{NavbarComponent},
  setup: ()=> {  // 每次刷新页面 这个都会执行一次
    const store = useStore()
    window.addEventListener("beforeunload",()=>{
      // 在页面卸载前触发
      localStorage.setItem("userStore",JSON.stringify(store.state))
    })
    localStorage.getItem("userStore") && store.replaceState(Object.assign(store.state,JSON.parse(localStorage.getItem("userStore"))));
    CheckIsLogin(store)
  }
}

</script>

<style>
</style>
