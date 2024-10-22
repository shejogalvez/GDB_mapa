<template>
  <div id="appp">
    <router-view :key="$route.path"></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
/* Add any global styles here */
</style>

