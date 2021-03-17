<template>
  <div class="box">
    <v-icon x-large :class="['iconn', 'white--text', color]">{{icon}}</v-icon>
    <div class="content">
      <h1>{{title}}</h1>
      <p>{{text}}</p>
    </div>
  </div>
</template>

<script>
export default {
    props: ['title', 'text', 'icon', 'color']
}
</script>

<style scoped>

.box {
  width: 100%;
  border: 1px solid black;
  display: flex;
  height: 100px;
}

.iconn {
  border: 1px solid black;
  height: 100px;
  width: 100px;
}

.content {
  width: auto;
}

</style>
