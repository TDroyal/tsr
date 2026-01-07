<template>
  <ContentComponent>
    <div class="card">
      <div class="card-body">
        首页
      </div>
    </div>
  </ContentComponent>
</template>

<script>
// @ is an alias to /src
// import HelloWorld from '@/components/HelloWorld.vue'
import ContentComponent from '@/components/ContentComponent.vue'
export default {
  name: 'HomeView',
  components: {
    ContentComponent,
  }
}
</script>
