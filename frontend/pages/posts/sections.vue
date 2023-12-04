<template>
<div>
  <!-- add tier button start -->
  <div class="text-right">
    <fm-button type="primary" @click="openFormDialog()">
      <icon-plus class="mr-1" :size="16"></icon-plus>
      Add a section
    </fm-button>
  </div>
  <!-- add tier button end -->

  <!-- tier list start -->
  <fm-table class="mt-8 table-fixed lg:table-auto" first-column-sticky>
    <colgroup>
      <col class="min-w-[140px]"> <!-- name -->
      <col class="min-w-[75px]"> <!-- post count -->
      <col class="min-w-[130px]"> <!-- created at -->
      <col class="w-[100px]"> <!-- edit -->
      <col class="w-[100px]"> <!-- delete -->
    </colgroup>
    <thead>
      <tr class="text-xs uppercase">
        <th>Name</th>
        <th class="!text-center">Post Count</th>
        <th>Created At</th>
        <th>Edit</th>
        <th>Delete</th>
      </tr>
    </thead>
    <tbody v-show="sections.length" class="text-sm">
      <tr v-for="section in sections" :key="section.id">
        <td>{{ section.title }}</td>
        <td class="!text-center">{{ section.post_count }}</td>
        <td>{{ $datetime(section.created_at) }}</td>
        <td>
          <fm-button size="sm" @click="openFormDialog(section)">Edit</fm-button>
        </td>
        <td>
          <fm-button size="sm" type="error" @click="deleteConfirm(section)">Delete</fm-button>
        </td>
      </tr>
    </tbody>
  </fm-table>

  <div
    v-if="!sections.length"
    class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-b-lg border border-t-0">
    <div class="text-center">
      <icon-library class="mx-auto stroke-1 h-16 w-16 mb-3"></icon-library>
      <div>Sections will appear here. <br> Click on <strong>Add a section</strong> to get started.</div>
    </div>
  </div>
  <!-- tier list end -->

  <!-- add/update tier start -->
  <fm-dialog v-model="isAddFormVisible" no-padding require-explicit-close>
    <!-- dialog heading start -->
    <template #header>
      {{ isEditing ? 'Edit Section' : 'Add Section' }}
    </template>
    <!-- dialog heading end -->

    <!-- dialog form and preview start -->
    <div v-loading.fullscreen="loading ? 'Saving...' : false" class="container py-6">
      <div class="row max-w-5xl mx-auto">
        <!-- form start -->
        <div class="col">
          <fm-form id="createOrEditSectionForm" :errors="formErrors" @submit.prevent="save">
            <fm-input v-model="form.title" uid="title" label="Section name" type="text" required></fm-input>
            <fm-input v-model="form.description" uid="description" label="Description" type="textarea"></fm-input>
          </fm-form>
        </div>
        <!-- form end -->
      </div>
    </div>
    <!-- dialog form and preview end -->

    <!-- dialog footer start -->
    <template #footer>
      <div class="text-right">
        <fm-button @click="isAddFormVisible = false;">Close</fm-button>
        <fm-button native-type="submit" form="createOrEditSectionForm" type="primary" :loading="loading">
          {{ isEditing ? 'Update section' : 'Create section' }}
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
import { mapActions, mapGetters } from 'vuex';
const initialFormState = () => ({
  title: '',
  description: ''
});
export default {
  data() {
    return {
      loading: false,
      isAddFormVisible: false,
      sectionToUpdate: null,
      form: initialFormState(),
      formErrors: {}
    };
  },
  head: {
    title: 'Manage tiers'
  },
  computed: {
    ...mapGetters('posts', ['sections']),

    isEditing() {
      return !!this.sectionToUpdate;
    }
  },
  watch: {
    async isAddFormVisible(isAddFormVisible) {
      if (!isAddFormVisible) {
        await this.$nextTick();
        Object.assign(this, {
          loading: false,
          isAddFormVisible: false,
          sectionToUpdate: null,
          form: initialFormState(),
          formErrors: {}
        });
      }
    }
  },
  created() {
    this.loadSections();
    if (this.$route.params.add === '1') {
      this.isAddFormVisible = true;
    }
  },
  methods: {
    ...mapActions('posts', ['loadSections', 'createSection', 'updateSection', 'deleteSection']),

    openFormDialog(section) {
      this.sectionToUpdate = section || null;
      if (this.sectionToUpdate) {
        this.form = pick(cloneDeep(this.sectionToUpdate), Object.keys(initialFormState()));
      }
      this.isAddFormVisible = true;
    },
    async save() {
      this.loading = true;

      // prepare payload
      const payload = cloneDeep(this.form);

      // make request to save
      let response;
      if (this.isEditing) response = await this.updateSection({ sectionId: this.sectionToUpdate.id, payload });
      else response = await this.createSection(payload);

      if (response.success) {
        this.$toast.success(this.isEditing ? 'Section updated successfully.' : 'Section created successfully.');
        await this.loadSections();
        this.isAddFormVisible = false;
      } else {
        this.formErrors = response.data;
      }

      this.loading = false;
    },
    async deleteConfirm(section) {
      try {
        await this.$confirm.error(`Are you sure you want to delete the section "${section.title}"? Associated posts will no longer have a section.`, 'Delete section');
      } catch (err) {
        return;
      }

      const { success } = await this.deleteSection(section.id);
      if (success) this.$toast.info('Section was deleted.');
    }
  }
};
</script>

