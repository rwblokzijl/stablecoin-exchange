<template>
  <div class="main">
    <div class="bar">
      <h1> EuroToken Exchange </h1>
    </div>
    <div class="container">
    <Exchange/>
    </div>
  </div>
</template>

<script>
import Exchange from '@/Exchange';

export default {
  name: 'App',

  components: {
    Exchange,
  },

  data: () => ({
    //
  }),
};
</script>

<style scoped>
.bar {
  background-color: #3c8dbc;
  padding-top: 20px;
  padding-bottom: 20px;
  text-align: center;
}

.bar>h1 {
  color: white;
  margin-top: 0px;
  margin-bottom: 0px;
}
</style>
