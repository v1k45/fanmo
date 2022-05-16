<template>
<creator-settings v-if="$auth.user.is_creator"></creator-settings>
<supporter-settings v-else></supporter-settings>
</template>

<script>
export default {

};
</script>
