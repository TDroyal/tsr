<template>
    <div class="mycontainer">
        <div class="background"></div>
        <div class="container">
            <div class="card">
                <div class="card-body" >
                    <slot></slot>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
export default {
    name:"ContentComponent",
}

</script>


<style scoped>

.mycontainer{
    position: relative;
    overflow: hidden;
}

.background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('../assets/background5.jpg');
    background-size: cover;
    z-index: 2;
}


.container {
    margin-top: 60px;
    background-color: #F7F8FA;
    max-height: none;
    min-height: 93.5vh;
    position: relative;
    background-color: transparent;  /* 设置为透明 */
    z-index: 3;  /*比.background大，并且是position: relative; 故在它的上面显示 */
}

.card {
    border: none;
    background-color: transparent;
    /* z-index: -2; */
}

.card-body {
    background-color: transparent;
}

/* 使用 CSS 的 position 属性将 slot 的内容定位到最上层，例如设置 position: relative; 并且使用 z-index 将其置于最上层。 */
.slot-content {
  position: relative;
  z-index: 100000;
}
</style>