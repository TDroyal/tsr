<!-- src/views/HomeView.vue -->
<template>
  <ContentComponent>
    <div class="home-view">
      <DataManager />
    </div>
  </ContentComponent>
</template>

<script>
import ContentComponent from '@/components/ContentComponent.vue'
import DataManager from '@/components/DataManager.vue'

export default {
  name: 'HomeView',
  components: {
    ContentComponent,
    DataManager
  },
  setup() {
    return {
      // 可以添加其他的响应式数据
    }
  }
}
</script>

<style scoped>
/* .home-view {
  padding: 20px;
} */
</style>