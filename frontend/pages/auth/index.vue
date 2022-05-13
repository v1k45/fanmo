<script>
export default {
  auth: true,
  created() {
    const { is_creator: isCreator } = this.$auth.user;
    if (isCreator) this.$router.replace({ name: 'dashboard' });
    else this.$router.replace({ name: 'feed' });
  },
  render: () => null
};
</script>
