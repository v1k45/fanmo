<template>
<div class="card compact shadow-md border-2 overflow-visible">
  <div class="card-body flex flex-row items-start pb-2">
    <div class="flex items-center">
      <div class="avatar">
        <div class="w-11 h-11 border rounded-full">
          <img :src="post.author_user.avatar.small">
        </div>
      </div>
      <div class="ml-3">
        <div class="text-lg font-bold">{{ post.title }}</div>
        <div class="text-xs text-base-content text-opacity-40">{{ post.author_user.username }} - {{ post.created_at }}</div>
      </div>
    </div>
    <div v-if="!isDeleted && $auth.loggedIn && post.author_user.username == $auth.user.username" class="dropdown dropdown-end ml-auto">
      <button class="m-1 btn btn-sm btn-ghost">
        <icon-more-horizontal></icon-more-horizontal>
      </button>
      <ul tabindex="0" class="p-2 shadow menu dropdown-content bg-base-100 rounded-box w-52">
        <!-- implement reporting later -->
        <li class="text-error"><a @click="deletePost(post.id)">Delete</a></li>
      </ul>
    </div>
  </div>
  <div class="card-body text-base pb-6">
    <template v-if="isDeleted">[deleted]</template>
    <template v-else-if="post.content">{{ post.content.text }}</template>
    <template v-else>Locked! {{ post.visibility }}</template>
  </div>
</div>
</template>

<script>
export default {
  props: {
    post: Object
  },
  data() {
    return {
      isDeleted: false
    };
  },
  methods: {
    async deletePost(postId) {
      if (!confirm('Are you sure you want to delete this post?')) {
        return;
      };

      await this.$axios.$delete(`/api/posts/${postId}/`);
      this.isDeleted = true;
    }
  }
};
</script>
