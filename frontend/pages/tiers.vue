<template>
<div>
  <div class="flex flex-wrap">
    <div class="mr-auto">
      <h1 class="text-2xl font-bold">Manage tiers</h1>
      <div class="mt-2 font-medium opacity-70">Create and manage your tiers, benefits and more</div>
    </div>
    <button class="mt-4 sm:mt-0 btn btn-wide btn-primary" @click="isAddTierVisible = true;">
      <IconPlus class="mr-1" :size="16"></IconPlus>
      Add a tier
    </button>
  </div>

  <div v-if="true" class="row">
    <div v-for="i in 10" :key="i" class="col-12 sm:col-6 md:col-6 lg:col-4 xl:col-3 gy-4">

      <div class="card compact border shadow-lg">
        <figure>
          <img src="https://picsum.photos/id/1005/400/250">
        </figure>
        <div class="card-body">
          <h2 class="card-title text-center">
            <icon-indian-rupee class="inline h-6"></icon-indian-rupee>500
            <div class="text-base truncate">Champion</div>
          </h2>
          <p class="mt-2">For the best of my fans!</p>
          <ul class="list-disc list-inside text-left mt-3">
            <li>Discord server</li>
            <li>Twitch badges</li>
            <li>Exclusive Twitch emojis</li>
          </ul>
          <div class="justify-center card-actions">
            <button class="btn btn-block">Edit</button>
          </div>
        </div>
      </div>

    </div>
  </div>

  <div v-else class="max-w-lg h-64 bg-gray-100 rounded-xl mx-auto mt-16 flex justify-center flex-col items-center">
    <div class="opacity-40 text-center">
      <icon-list-minus :size="64" class="mx-auto mb-3"></icon-list-minus>
      <div>Tiers will appear here. <br> Click on <strong>Add a tier</strong> to get started.</div>
    </div>
  </div>

  <add-tier v-model="isAddTierVisible"></add-tier>
</div>
</template>

<script>
export default {
  data() {
    return {
      isAddTierVisible: false
    };
  }
};
</script>
