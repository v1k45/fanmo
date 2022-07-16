<template>
<div class="flex justify-center items-center min-h-screen text-center bg-fm-primary text-white">
  <div>
    <div v-if="error.statusCode === 404">
      <h1 class="text-9xl text-white font-bold flex justify-center items-center animatecss animatecss-bounceInDown">
        4 <div class="h-28 w-28 mx-1 flex items-center justify-center rounded-full bg-white border-8 border-fm-success">
          <logo class="h-16 w-16" circle></logo>
        </div> 4
      </h1>
      <div class="text-3xl font-bold uppercase">Page not found</div>
    </div>
    <template v-else>An error occurred</template>
    <div class="text-black mt-8">
      <fm-button type="primary" class="mx-2 min-w-[150px]" @click="$router.go(-1)">
        <span class="text-lg">&larr; Back</span>
      </fm-button>
      <fm-button
        type="success" class="mx-2 min-w-[150px]"
        @click="$router.push({ name: $auth.loggedIn ? 'auth' : 'index' })">
        <span class="text-lg">{{ $auth.loggedIn ? 'Dashboard' : 'Home' }}</span>
      </fm-button>
    </div>
  </div>
</div>
</template>

<script>
export default {
  layout: 'empty',
  props: {
    error: { type: Object, required: true }
  }
};
</script>
