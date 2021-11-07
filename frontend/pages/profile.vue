<template>
<div>
  <div class="aspect-w-12 aspect-h-2 relative bg-black">
    <img class="object-cover h-full w-full absolute" src="https://picsum.photos/1200/600" alt="Cover photo">
  </div>
  <div class="-mt-6 container flex items-center">
    <div class="avatar rounded-full p-1 bg-white">
      <div class="w-32 h-32 rounded-full">
        <img src="http://daisyui.com/tailwind-css-component-profile-5@40w.png">
      </div>
    </div>
    <div class="ml-3">
      <div class="text-2xl font-bold">dumptyd</div>
      <div class="flex items-center"><icon-heart class="mr-2 fill-current text-error" :size="16"></icon-heart> 136 followers</div>
    </div>
  </div>
</div>
</template>

<script>
export default {
  layout: 'default-no-container'
};
</script>

<style>

</style>
