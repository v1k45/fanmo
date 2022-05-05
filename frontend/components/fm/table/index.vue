<template>
<div class="fm-table" :class="{ 'fm-table--first-column-sticky': firstColumnSticky }">
  <table>
    <slot></slot>
  </table>
</div>
</template>

<script>
export default {
  props: {
    firstColumnSticky: { type: Boolean, default: false }
  }
};
</script>
<style lang="scss">
.fm-table {
  @apply overflow-auto;

  table {
    @apply w-full border-separate;
    border-spacing: 0;
  }
  th {
    @apply text-left;
  }
  thead {
    @apply bg-gray-100 relative top-0 z-10;
  }
  thead th {
    @apply bg-gray-100 p-3 border-t border-b border-r relative;
    &:first-child {
      @apply rounded-tl-lg border-l;
    }
    &:last-child {
      @apply rounded-tr-lg border-r;
    }
  }
  tr {
  }
  td, th {
    @apply px-3 py-3 border-b break-words;
  }
  tbody {
    td, th {
      &:first-child {
        @apply border-l;
      }
      &:last-child {
        @apply border-r;
      }
    }
    tr:last-child {
      td, th {
        &:first-child {
          @apply rounded-bl-lg;
        }
        &:last-child {
          @apply rounded-br-lg;
        }
      }
    }
  }
}
.fm-table--first-column-sticky {
  th:first-child, td:first-child {
    @apply sticky left-0 z-10;
  }
  tbody th:first-child, td:first-child {
    @apply bg-white;
  }
}
</style>
