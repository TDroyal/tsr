<template>
  <ContentComponent>
    <div class="login-container">
      <div class="row justify-content-center min-vh-100">
        <div class="col-12 col-md-5 col-lg-4">
          <div class="login-card">
            <!-- 登录卡片头部 -->
            <div class="login-header">
              <div class="login-logo">
                <i class="fas fa-chart-line"></i>
              </div>
              <h3 class="login-title">时序系统</h3>
              <p class="login-subtitle">欢迎回来，请登录您的账户</p>
            </div>
            
            <!-- 登录卡片主体 -->
            <div class="login-body">
              <!-- 登录表单 -->
              <form @submit.prevent="login" class="login-form">
                <!-- 用户名输入框 -->
                <div class="form-group mb-4">
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="fas fa-user"></i>
                    </span>
                    <input 
                      v-model="username" 
                      type="text" 
                      class="form-control" 
                      id="username" 
                      placeholder="请输入用户名" 
                      autocomplete="username" 
                      required
                    >
                  </div>
                </div>
                
                <!-- 密码输入框 -->
                <div class="form-group mb-4">
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="fas fa-lock"></i>
                    </span>
                    <input 
                      v-model="password" 
                      :type="showPassword ? 'text' : 'password'" 
                      class="form-control" 
                      id="password" 
                      placeholder="请输入密码" 
                      autocomplete="current-password" 
                      required
                    >
                    <button 
                      type="button" 
                      class="btn btn-outline-secondary password-toggle"
                      @click="togglePassword"
                    >
                      <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                    </button>
                  </div>
                </div>
                
                <!-- 错误消息 -->
                <div v-if="error_message" class="alert alert-danger alert-dismissible fade show" role="alert">
                  <i class="fas fa-exclamation-circle me-2"></i>
                  {{ error_message }}
                  <button type="button" class="btn-close" @click="error_message = ''"></button>
                </div>
                
                <!-- 登录按钮 -->
                <div class="d-grid gap-2">
                  <button 
                    type="submit" 
                    class="btn btn-primary btn-login"
                    :disabled="loading"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="fas fa-sign-in-alt me-2"></i>
                    {{ loading ? '登录中...' : '登录' }}
                  </button>
                </div>
                
                <!-- 分隔线 -->
                <div class="divider my-4">
                  <span>或</span>
                </div>
                
                <!-- 快速提示 -->
                <div class="login-hint text-center">
                  <p class="mb-0 text-muted">
                    <i class="fas fa-info-circle me-1"></i>
                    使用 royal_111/123456 或 admin/123456 进行测试
                  </p>
                </div>
              </form>
            </div>
            
            <!-- 登录卡片底部 -->
            <div class="login-footer text-center">
              <p class="mb-0 text-muted">
                <small>© 2026 时序系统 v1.0.0</small>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </ContentComponent>
</template>

<script>
import ContentComponent from '@/components/ContentComponent.vue'
import { useStore } from 'vuex'
import router from '@/router/index'
import { ref } from 'vue'
// import {CheckIsLogin} from '@/config/util'
export default {
  name: 'LoginView',
  components: {
    ContentComponent,
  },
  setup() {
    const store = useStore()
    const username = ref('')
    const password = ref('')
    const error_message = ref('')
    const showPassword = ref(false)
    const loading = ref(false)

    // if(CheckIsLogin(store)) {
    //   router.push({ name: "home" })
    //   return
    // } else {
    //   router.push({name: "login"})
    // }

    const login = () => {
      error_message.value = ""
      loading.value = true
      
      store.dispatch("login", {
        username: username.value,
        password: password.value,
        success() {
          loading.value = false
          // 登录成功提示
          store.commit('setToast', {
            show: true,
            message: '登录成功！',
            type: 'success'
          })
          router.push({ name: "home" })
        },
        error: (msg) => {
          loading.value = false
          error_message.value = msg
        }
      })
    }

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    return {
      username,
      password,
      error_message,
      showPassword,
      loading,
      login,
      togglePassword,
    }
  }
}
</script>

<style scoped>
.login-container {
  /* background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); */
  min-height: 100vh;
  padding: 20px;
}

/* 登录卡片样式 */
.login-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
}

/* 头部样式 */
.login-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 40px 30px 30px;
  position: relative;
  overflow: hidden;
}

.login-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
  pointer-events: none;
}

.login-logo {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 36px;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.login-subtitle {
  font-size: 15px;
  opacity: 0.9;
  margin-bottom: 0;
  font-weight: 300;
}

/* 主体样式 */
.login-body {
  padding: 40px 30px 30px;
}

.login-form {
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 输入框样式 */
.input-group {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
  transition: all 0.3s;
}

.input-group:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.input-group-text {
  background-color: #f8f9fa;
  border: none;
  padding: 0 20px;
  color: #667eea;
  font-size: 16px;
  min-width: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-control {
  border: none;
  padding: 15px 20px;
  font-size: 16px;
  background: transparent;
}

.form-control:focus {
  box-shadow: none;
  background: transparent;
}

.form-control::placeholder {
  color: #999;
  font-weight: 300;
}

/* 密码显示/隐藏按钮 */
.password-toggle {
  background-color: #f8f9fa;
  border: none;
  padding: 0 20px;
  color: #6c757d;
  transition: all 0.3s;
  border-left: 1px solid #e0e0e0;
}

.password-toggle:hover {
  background-color: #e9ecef;
  color: #495057;
}

/* 错误提示 */
.alert-danger {
  border-radius: 10px;
  border: none;
  background-color: #fee;
  color: #dc3545;
  padding: 12px 20px;
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.btn-close:focus {
  box-shadow: none;
}

/* 登录按钮 */
.btn-login {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 15px 20px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  transition: all 0.3s;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.btn-login:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-login:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 分隔线 */
.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #999;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e0e0e0;
}

.divider span {
  padding: 0 20px;
  font-size: 14px;
  font-weight: 300;
}

/* 提示文本 */
.login-hint {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 8px;
  font-size: 14px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.8; }
  100% { opacity: 1; }
}

/* 底部样式 */
.login-footer {
  padding: 20px 30px;
  background-color: #f8f9fa;
  border-top: 1px solid #e0e0e0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 10px;
  }
  
  .login-header {
    padding: 30px 20px 20px;
  }
  
  .login-body {
    padding: 30px 20px 20px;
  }
  
  .login-logo {
    width: 60px;
    height: 60px;
    font-size: 28px;
  }
  
  .login-title {
    font-size: 24px;
  }
  
  .login-subtitle {
    font-size: 14px;
  }
  
  .form-control {
    padding: 12px 15px;
    font-size: 15px;
  }
  
  .input-group-text {
    padding: 0 15px;
    min-width: 45px;
  }
  
  .password-toggle {
    padding: 0 15px;
  }
  
  .btn-login {
    padding: 12px 20px;
    font-size: 15px;
  }
}

@media (max-width: 576px) {
  .col-12 {
    padding: 0;
  }
  
  .login-card {
    border-radius: 15px;
  }
  
  .login-header {
    padding: 25px 15px 15px;
  }
  
  .login-body {
    padding: 25px 15px 15px;
  }
}
</style>