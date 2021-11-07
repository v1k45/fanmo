<template>
<div>
  <h1 class="text-2xl font-bold">Subscribers (317)</h1>
  <div class="mt-2 font-medium opacity-70">View and manage your subscribers</div>

  <div class="form-control mt-6">
    <input type="text" placeholder="Search subscribers" class="input input-bordered">
  </div>
  <div class="overflow-x-auto mt-6 border rounded-lg">
    <table class="table table-zebra w-full">
      <thead>
        <tr>
          <th>Subscriber name</th>
          <th align="center">Tier</th>
          <th>Last paid</th>
          <th>Last paid on</th>
          <th>Lifetime paid</th>
          <th align="center">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th scope="row">
            <div class="flex items-center space-x-3">
              <div class="avatar">
                <div class="w-12 h-12 mask mask-squircle">
                  <img src="http://daisyui.com/tailwind-css-component-profile-2@56w.png" alt="Avatar Tailwind CSS Component">
                </div>
              </div>
              <div class="font-bold">Hart Hagerty</div>
            </div>
          </th>
          <td align="center">
            <div class="badge badge-info w-32">Gold</div>
          </td>
          <td><money-display>300</money-display></td>
          <td>21st Aug, 2021</td>
          <td><money-display>4350.94</money-display></td>
          <td align="center">
            <div class="badge badge-success badge-lg w-24">Active</div>
          </td>
        </tr>

        <tr>
          <th scope="row">
            <div class="flex items-center space-x-3">
              <div class="avatar">
                <div class="w-12 h-12 mask mask-squircle">
                  <img src="http://daisyui.com/tailwind-css-component-profile-3@56w.png" alt="Avatar Tailwind CSS Component">
                </div>
              </div>
              <div class="font-bold">
                Brice Swyre
              </div>
            </div>
          </th>
          <td align="center">
            <div class="badge badge-info w-32">Gold</div>
          </td>
          <td><money-display>300</money-display></td>
          <td>21st Aug, 2021</td>
          <td><money-display>4350.94</money-display></td>
          <td align="center">
            <div class="badge badge-success badge-lg w-24">Active</div>
          </td>
        </tr>

        <tr>
          <th scope="row">
            <div class="flex items-center space-x-3">
              <div class="avatar">
                <div class="w-12 h-12 mask mask-squircle">
                  <img src="http://daisyui.com/tailwind-css-component-profile-4@56w.png" alt="Avatar Tailwind CSS Component">
                </div>
              </div>
              <div class="font-bold">
                Marjy Ferencz
              </div>
            </div>
          </th>
          <td align="center">
            <div class="badge badge-info w-32">Gold</div>
          </td>
          <td><money-display>300</money-display></td>
          <td>21st Aug, 2021</td>
          <td><money-display>4350.94</money-display></td>
          <td align="center">
            <div class="badge badge-success badge-lg w-24">Active</div>
          </td>
        </tr>

        <tr>
          <th scope="row">
            <div class="flex items-center space-x-3">
              <div class="avatar">
                <div class="w-12 h-12 mask mask-squircle">
                  <img src="http://daisyui.com/tailwind-css-component-profile-5@56w.png" alt="Avatar Tailwind CSS Component">
                </div>
              </div>
              <div class="font-bold">
                Yancy Tear
              </div>
            </div>
          </th>
          <td align="center">
            <div class="badge badge-info w-32">Gold</div>
          </td>
          <td><money-display>300</money-display></td>
          <td>21st Aug, 2021</td>
          <td><money-display>4350.94</money-display></td>
          <td align="center">
            <div class="badge badge-success badge-lg w-24">Active</div>
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <th>Subscriber name</th>
          <th align="center">Tier</th>
          <th>Last paid</th>
          <th>Last paid on</th>
          <th>Lifetime paid</th>
          <th align="center">Status</th>
        </tr>
      </tfoot>
    </table>
  </div>
</div>
</template>

<script>
export default {

};
</script>
