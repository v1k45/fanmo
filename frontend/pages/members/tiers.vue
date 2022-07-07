<template>
<div>
  <!-- add tier button start -->
  <div class="text-right">
    <fm-button type="primary" @click="openTierDialog()">
      <icon-plus class="mr-1" :size="16"></icon-plus>
      Add a tier
    </fm-button>
  </div>
  <!-- add tier button end -->

  <!-- tier list start -->
  <div v-if="tiers && tiers.count" class="row g-3 mt-4">
    <div v-for="tier in tiers.results" :key="tier.id" class="col-12 md:col-6 lg:col-6 xl:col-4">
      <profile-tier-card :tier="tier" class="h-full max-w-[360px] mx-auto" edit-mode @edit="openTierDialog(tier)"></profile-tier-card>
    </div>
  </div>

  <div v-else-if="tiers && !tiers.count" class="max-w-lg h-64 bg-gray-100 rounded-xl mx-auto mt-16 flex justify-center flex-col items-center">
    <div class="text-center">
      <icon-crown class="mx-auto stroke-1 h-16 w-16 mb-3"></icon-crown>
      <div>Tiers will appear here. <br> Click on <strong>Add a tier</strong> to get started.</div>
    </div>
  </div>
  <!-- tier list end -->

  <!-- add/update tier start -->
  <fm-dialog v-model="isAddTierVisible" fullscreen no-padding>
    <!-- dialog heading start -->
    <template #header>
      <div class="relative">
        <div class="container max-w-5xl">{{ isEditing ? 'Edit tier' : 'Add a tier' }}</div>
        <logo class="h-5 absolute right-10 top-1"></logo>
      </div>
    </template>
    <!-- dialog heading end -->

    <!-- dialog form and preview start -->
    <div v-loading.fullscreen="loading ? 'Saving...' : false" class="container pt-6 pb-24">
      <div class="row max-w-5xl mx-auto">

        <!-- form start -->
        <div class="col">
          <fm-form id="createOrEditTierForm" :errors="tierFormErrors" @submit.prevent="save">
            <fm-input v-model="tierForm.name" uid="name" label="Tier name" type="text" required></fm-input>

            <!-- amount start -->
            <fm-input v-model.number="tierForm.amount" uid="amount" label="Monthly price" type="number" min="1" max="10000000" required>
              <template v-if="tierForm.amount > 5000" #after-label>
                <fm-alert type="warning" class="mt-1 mb-2 text-sm">
                  Because of RBI guidelines, membership plans higher than {{ $currency(5000) }} will require additional authentication from your supporters every subscription cycle.
                  This could lead to lower renewals.
                </fm-alert>
              </template>
              <template #prepend>
                <icon-indian-rupee class="w-em"></icon-indian-rupee>
              </template>
            </fm-input>
            <!-- amount end -->

            <!-- image start -->
            <fm-input v-model="tierForm.cover_base64" uid="cover_base64" label="Tier image" type="file" accept="images/*">
              <template #label>
                <label class="mr-3">Tier image</label>
                <div class="text-sm text-gray-500">Tier image is optional but we highly recommend adding one to establish and emphasize your brand and community.</div>
              </template>
            </fm-input>

            <div v-if="tierForm.cover_base64" class="my-6">
              <fm-input v-model="tierForm.cover_background_style" horizontal label="Image style" native-value="contain" type="radio">Contain</fm-input>
              <fm-input v-model="tierForm.cover_background_style" uid="cover_background_style" native-value="cover" horizontal type="radio">Cover</fm-input>
            </div>
            <!-- image end -->

            <fm-input v-model="tierForm.description" uid="description" label="Description" type="textarea" required></fm-input>

            <!-- benefits start -->
            <div class="mt-6">
              <label class="block mb-2">Benefits</label>
              <div v-for="(benefit, idx) in tierForm.benefits" :key="idx" class="flex items-center mb-2">
                <div class="flex-1 mr-3">
                  <fm-input v-model="tierForm.benefits[idx]" :uid="`benefits[${idx}]`" type="text" placeholder="Eg. Discord access, Behind the scenes, Early access, etc."></fm-input>
                </div>
                <div class="self-end mb-2">
                  <fm-button size="sm" circle @click="tierForm.benefits.splice(idx, 1)">
                    <icon-x class="w-4 h-4 text-fm-error"></icon-x>
                  </fm-button>
                </div>
              </div>
              <div class="text-right mb-3">
                <fm-button size="sm" @click="tierForm.benefits.push('')">
                  <template v-if="tierForm.benefits.length">Add another</template>
                  <template v-else>Add a benefit</template>
                </fm-button>
              </div>
            </div>
            <!-- benefits end -->

            <hr class="my-4">

            <!-- settings start -->
            <div>
              <div class="mb-4">Settings</div>
              <fm-input v-model="tierForm.is_public" uid="is_public" type="checkbox">Public</fm-input>
              <fm-input v-model="tierForm.is_recommended" uid="is_recommended" class="!mt-2" type="checkbox">Recommended</fm-input>
            </div>
            <!-- settings end -->

            <hr class="my-4">

            <!-- welcome message start -->
            <fm-input v-model="tierForm.welcome_message" uid="welcome_message" type="textarea" rows="5" required>
              <template #label>
                <div class="flex">
                  <div class="mr-auto">
                    <label class="mr-3">Welcome message</label>
                    <div class="text-sm text-gray-500">This will be shown after the payment and in the welcome email.</div>
                  </div>
                  <div>
                    <fm-button size="sm" @click="isPaymentSuccessPreviewVisible = true;">Preview</fm-button>
                  </div>
                </div>
              </template>
            </fm-input>
            <!-- welcome message end -->

          </fm-form>
        </div>
        <!-- form end -->

        <!-- preview start -->
        <div class="hidden lg:block col-auto">
          <div class="bg-gray-50 min-h-full rounded-lg px-6 py-4">
            <!-- TODO: once breakpoint service is available, add a preview tab for phones -->
            <div class="text-lg font-bold mb-4">Preview</div>
            <!-- preview card start -->
            <div class="w-[360px] max-w-full mx-auto">
              <div class="w-full"></div>
              <profile-tier-card :tier="previewTier" @subscribe-click="isPaymentSuccessPreviewVisible = true;"></profile-tier-card>
            </div>
            <!-- preview card end -->
          </div>
        </div>
        <!-- preview end -->

      </div>
    </div>
    <!-- dialog form and preview end -->

    <!-- nested dialog start -->
    <profile-payment-success
      v-model="isPaymentSuccessPreviewVisible"
      support-type="membership"
      :user="$auth.user"
      :tier="previewTier"
      :success-message="tierForm.welcome_message"
      show-close>
    </profile-payment-success>
    <!-- nested dialog end -->


    <!-- dialog footer start -->
    <template #footer>
      <div class="text-right">
        <fm-button @click="isAddTierVisible = false;">Close</fm-button>
        <fm-button native-type="submit" form="createOrEditTierForm" type="primary" :loading="loading">
          {{ isEditing ? 'Update tier' : 'Create tier' }}
        </fm-button>
      </div>
    </template>
    <!-- dialog footer end -->

  </fm-dialog>
  <!-- add/update tier end -->

</div>
</template>

<script>
import pick from 'lodash/pick';
import cloneDeep from 'lodash/cloneDeep';
import { mapActions, mapState } from 'vuex';
import { getBase64FromFile } from '~/utils';
const initialFormState = () => ({
  name: '',
  amount: '',
  cover_base64: '',
  cover_background_style: 'contain',
  description: '',
  welcome_message: 'Thank you for supporting me! 🎉',
  benefits: [''],
  is_public: true,
  is_recommended: false
});
export default {
  data() {
    return {
      loading: false,
      isAddTierVisible: false,
      tierToUpdate: null,
      tierForm: initialFormState(),
      tierFormErrors: {},
      isPaymentSuccessPreviewVisible: false
    };
  },
  head: {
    title: 'Manage tiers'
  },
  computed: {
    ...mapState('memberships', ['tiers']),

    isEditing() {
      return !!this.tierToUpdate;
    },
    previewTier() {
      const { tierForm, isEditing } = this;
      const cover = (() => {
        if (isEditing) {
          if (tierForm.cover_base64 && typeof tierForm.cover_base64 !== 'string') return URL.createObjectURL(tierForm.cover_base64);
          else return tierForm.cover_base64;
        } else {
          return tierForm.cover_base64 && typeof tierForm.cover_base64 !== 'string' ? URL.createObjectURL(tierForm.cover_base64) : '';
        }
      })();
      return {
        id: Date.now(),
        name: tierForm.name,
        amount: tierForm.amount || 0,
        cover: cover ? { big: cover, full: cover, medium: cover, small: cover } : '',
        cover_background_style: tierForm.cover_background_style,
        description: tierForm.description,
        welcome_message: tierForm.welcome_message,
        benefits: tierForm.benefits,
        is_public: tierForm.is_public,
        is_recommended: tierForm.is_recommended
      };
    }
  },
  watch: {
    async isAddTierVisible(isAddTierVisible) {
      if (!isAddTierVisible) {
        await this.$nextTick();
        Object.assign(this, {
          loading: false,
          isAddTierVisible: false,
          tierToUpdate: null,
          tierForm: initialFormState(),
          tierFormErrors: {},
          isPaymentSuccessPreviewVisible: false
        });
      }
    }
  },
  created() {
    this.fetchTiers();
  },
  methods: {
    ...mapActions('memberships', ['fetchTiers', 'createTier', 'updateTier']),

    openTierDialog(tier) {
      this.tierToUpdate = tier || null;
      if (this.tierToUpdate) {
        this.tierForm = pick(cloneDeep(this.tierToUpdate), Object.keys(initialFormState()));
        this.$set(this.tierForm, 'cover_base64', this.tierToUpdate.cover ? this.tierToUpdate.cover.full : '');
      }
      this.isAddTierVisible = true;
    },
    async save() {
      this.loading = true;

      // prepare payload
      const payload = cloneDeep(this.tierForm);
      payload.benefits = payload.benefits.filter(benefit => !!benefit);
      // adding new
      if (payload.cover_base64 && typeof payload.cover_base64 !== 'string') payload.cover_base64 = await getBase64FromFile(payload.cover_base64);
      // deleting existing
      // eslint-disable-next-line brace-style
      else if (this.tierToUpdate && this.tierToUpdate.cover && !payload.cover_base64) { /* nothing */ }
      // unchanged
      else delete payload.cover_base64;

      // make request to save
      let response;
      if (this.isEditing) response = await this.updateTier({ tierId: this.tierToUpdate.id, payload });
      else response = await this.createTier(payload);

      if (response.success) {
        this.$toast.success(this.isEditing ? 'Tier updated successfully.' : 'Tier created successfully.');
        await this.fetchTiers();
        this.isAddTierVisible = false;
      } else {
        this.tierFormErrors = response.data;
      }

      this.loading = false;
    }
  }
};
</script>
