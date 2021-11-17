<template>
<div>
  <div class="flex flex-wrap">
    <div class="mr-auto">
      <h1 class="text-2xl font-bold">Manage tiers ({{ tiers.count }})</h1>
      <div class="mt-2 font-medium opacity-70">Create and manage your tiers, benefits and more</div>
    </div>
    <button class="mt-4 sm:mt-0 btn btn-wide btn-primary" @click="openTierDialog()">
      <IconPlus class="mr-1" :size="16"></IconPlus>
      Add a tier
    </button>
  </div>

  <div v-if="tiers.count" class="row g-4 mt-4">
    <tier
      v-for="tier in tiers.results" :key="tier.id" :user="$auth.user"
      :tier="tier" self-mode @edit="openTierDialog(tier)">
    </tier>
  </div>

  <div v-else class="max-w-lg h-64 bg-gray-100 rounded-xl mx-auto mt-16 flex justify-center flex-col items-center">
    <div class="opacity-40 text-center">
      <icon-list-minus :size="64" class="mx-auto mb-3"></icon-list-minus>
      <div>Tiers will appear here. <br> Click on <strong>Add a tier</strong> to get started.</div>
    </div>
  </div>

  <add-tier v-model="isAddTierVisible" :tier-to-update="tierToUpdate" @update="updateTiers"></add-tier>
</div>
</template>

<script>
export default {
  async asyncData({ $axios }) {
    const tiers = await $axios.$get('/api/tiers/');
    return { tiers };
  },
  data() {
    return {
      isAddTierVisible: false,
      tierToUpdate: null
    };
  },
  head: {
    title: 'Manage tiers'
  },
  methods: {
    openTierDialog(tier) {
      this.tierToUpdate = tier || null;
      this.isAddTierVisible = true;
    },
    updateTiers(createdOrUpdatedTier) {
      const existingTierIdx = this.tiers.results.findIndex(tier => tier.id === createdOrUpdatedTier.id);
      if (existingTierIdx >= 0) this.tiers.results.splice(existingTierIdx, 1, createdOrUpdatedTier);
      else this.tiers.results.unshift(createdOrUpdatedTier);
      this.tiers.count = this.tiers.results.length;
    }
  }
};
</script>
