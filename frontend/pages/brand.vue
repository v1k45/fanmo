<template>
<fm-markdown-styled class="bg-white p-6 rounded-lg">
  <h1 class="font-title text-3xl text-center mb-2">Brand Kit</h1>
  <p class="text-center mb-2">Make your Fanmo page link prettier when you share it with your fans.</p>
  <p>You might be looking to use Fanmo brand colour, logo or buttons in your Videos and Posts on platforms such as YouTube, Twitter, Instagram etc. Follow these simple guidelines while promoting your page to make the most impact.</p>
  <h2 class="text-xl my-4">Colours</h2>
  <p>To emphasize Fanmo brand, always use the background colour specified below.</p>
  <div class="flex text-center">
    <div class="w-1/3">
      <div class="bg-fm-primary w-full h-24"></div>
      <div class="m-2">#6B68F9 (Brand Colour)</div>
    </div>
    <div class="w-1/3">
      <div class="bg-white w-full h-24"></div>
      <div class="m-2">#FFFFFF (Brand White)</div>
    </div>
    <div class="w-1/3">
      <div class="bg-gray-800 w-full h-24"></div>
      <div class="m-2">#6A6C75 (Brand Black)</div>
    </div>
  </div>
  <h2 class="text-xl my-4">Brand Assets</h2>
  <p>Our brand assets include high resolution Logo, Icon and Buttons in PNG and SVG formats. You can resize them as per your needs and use it when you share your Fanmo page.</p>
  <div class="text-center mb-4">
    <img class="h-40 my-4 mx-auto unstyled" src="~/assets/cover.svg">
    <a class="unstyled text-white" href="/fanmo_brand_assets.zip">
      <fm-button type="primary">Download Assets</fm-button>
    </a>
  </div>
  <p>If you are looking for something specific and the asset files don't meet your needs, feel free to reach out to us on <a href="mailto:help@fanmo.in">help@fanmo.in</a>.</p>
</fm-markdown-styled>
</template>


<script>
export default {
  auth: false,
  head: {
    title: 'Brand Kit'
  }
};
</script>
