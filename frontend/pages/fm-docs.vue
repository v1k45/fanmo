<template>
<section>

  <div class="mt-12">
    <h2 class="text-2xl font-title font-bold mb-6">Toggle section visibility to keep things manageable</h2>
    <fm-input v-model="sectionAll" type="checkbox" horizontal>All</fm-input>
    <fm-input
      v-for="(_, key) in sections" :key="key" v-model="sections[key]" type="checkbox" horizontal>
      <span class="capitalize">{{ key }}</span>
    </fm-input>
  </div>

  <hr class="my-16">

  <!-- button start -->
  <section v-show="sections.button" class="pb-12 mb-12 border-b-2">
    <h2 class="text-3xl font-title font-bold mb-6">Button</h2>

    <fm-button type="primary">Primary</fm-button>
    <fm-button type="success">Success</fm-button>
    <fm-button type="error">Error</fm-button>
    <fm-button type="warning">Warning</fm-button>
    <fm-button type="info">Info</fm-button>
    <fm-button>Default</fm-button>
    <fm-button type="link">Link</fm-button>

    <br><br>

    <fm-button disabled type="primary">Primary</fm-button>
    <fm-button disabled type="success">Success</fm-button>
    <fm-button disabled type="error">Error</fm-button>
    <fm-button disabled type="warning">Warning</fm-button>
    <fm-button disabled type="info">Info</fm-button>
    <fm-button disabled>Default</fm-button>
    <fm-button disabled type="link">Link</fm-button>
  </section>
  <!-- button end -->

  <!-- inputs start -->
  <section v-show="sections.input" class="pb-12 mb-12 border-b-2">
    <h2 class="text-3xl font-title font-bold mb-6">Input, textarea, OTP input and checkbox</h2>

    <fm-input v-model="model" class="max-w-md" label="Display name" placeholder="Eg. John Doe"></fm-input>
    <div class="mt-8 flex max-w-md">
      <div class="flex-grow mr-2"><fm-input v-model="model" placeholder="Eg. John Doe"></fm-input></div>
      <div><fm-button type="primary">Submit</fm-button></div>
    </div>
    <fm-input v-model="model" error="Invalid name. Only alphanumeric characters are allowed." class="max-w-md" label="Display name" placeholder="Eg. John Doe"></fm-input>
    <fm-input v-model="model" class="max-w-md" type="password" label="Password"></fm-input>
    <fm-input v-model="model" class="max-w-md" type="textarea" label="About you" placeholder="I grew up in a shithole..."></fm-input>
    <fm-input v-model="model" class="max-w-md" type="checkbox" label="Do you agree to T&amp;C?">I agree to terms and conditions</fm-input>
    <fm-input v-model="model" type="otp" label="Enter OTP"></fm-input>
  </section>
  <!-- inputs end -->

  <!-- alerts start -->
  <section v-show="sections.alert" class="pb-12 mb-12 border-b-2">
    <h2 class="text-3xl font-title font-bold mb-6">Alert</h2>
    <div>
      <fm-button type="info" @click="$toast.info(lorem(10))">Info</fm-button>
      <fm-button type="warning" @click="$toast.warning(lorem(10))">Warning</fm-button>
      <fm-button type="error" @click="$toast.error(lorem(10))">Error</fm-button>
      <fm-button type="success" @click="$toast.success(lorem(10))">Success</fm-button>
    </div>
    <fm-input v-model="misc.alert.clamped" type="checkbox" class="my-6">Clamped</fm-input>
    <fm-alert :clamped="misc.alert.clamped" title="A simple info message - keep it short" type="info">Lorem ipsum dolor sit amet consectetur adipisicing elit. Architecto vel perferendis delectus assumenda doloribus dolorum facere, neque asperiores sapiente iusto.!</fm-alert>
    <fm-alert :clamped="misc.alert.clamped" title="A simple warning message - keep it short" type="warning">Lorem ipsum dolor sit amet consectetur adipisicing elit. Architecto vel perferendis delectus assumenda doloribus dolorum facere, neque asperiores sapiente iusto.!</fm-alert>
    <fm-alert :clamped="misc.alert.clamped" title="A simple error message - keep it short" type="error">Lorem ipsum dolor sit amet consectetur adipisicing elit. Architecto vel perferendis delectus assumenda doloribus dolorum facere, neque asperiores sapiente iusto.!</fm-alert>
    <fm-alert :clamped="misc.alert.clamped" title="A simple success message - keep it short" type="success">Lorem ipsum dolor sit amet consectetur adipisicing elit. Architecto vel perferendis delectus assumenda doloribus dolorum facere, neque asperiores sapiente iusto.!</fm-alert>
  </section>
  <!-- alerts end -->


  <!-- dropdown start -->
  <!-- <section class="pb-12 mb-12 border-b-2">
    <h2 class="text-3xl font-title font-bold mb-6">Dropdown</h2>

    <fm-dropdown>
      <fm-button type="primary">Click me</fm-button>

      <template #items>
        <fm-dropdown-item>Item 1</fm-dropdown-item>
        <fm-dropdown-item>Item 2</fm-dropdown-item>
        <fm-dropdown-item>Item 3</fm-dropdown-item>
        <fm-dropdown-item>Item 4</fm-dropdown-item>
        <fm-dropdown-divider></fm-dropdown-divider>
        <fm-dropdown-item>Item 5</fm-dropdown-item>
      </template>
    </fm-dropdown>

  </section> -->
  <!-- dropdown end -->

  <!-- wizard start -->
  <section v-show="sections.wizard" class="pb-12 mb-12 border-b-2">
    <h2 class="text-3xl font-title font-bold mb-6">Wizard</h2>
    <fm-wizard>
      <fm-wizard-step :id="1" :current="misc.wizard.current === 1" :finished="misc.wizard.current > 1">Create account</fm-wizard-step>
      <fm-wizard-step :id="2" :current="misc.wizard.current === 2" :finished="misc.wizard.current > 2">Complete profile</fm-wizard-step>
      <fm-wizard-step :id="3" :current="misc.wizard.current === 3" :finished="misc.wizard.current > 3">Add payment details</fm-wizard-step>
    </fm-wizard>
    <div class="flex justify-center mt-6">
      <fm-button class="w-36 mr-6" @click="misc.wizard.current = misc.wizard.current === 0 ? 0 : (misc.wizard.current - 1)">Previous</fm-button>
      <fm-button class="w-36" @click="misc.wizard.current = misc.wizard.current === 4 ? 4 : (misc.wizard.current + 1)">Next</fm-button>
    </div>
  </section>
  <!-- wizard end -->

  <!-- dialogs start -->
  <section v-show="sections.dialog" class="pb-12 mb-12 border-b-2">
    <h2 class="text-3xl font-title font-bold mb-6">Dialog</h2>

    <fm-button type="primary" @click="misc.dialog.isVisible = true;">Open dialog</fm-button>

    <h2 class="text-xl font-title font-bold mt-6">Alert service</h2>
    <div class="mt-3">
      <fm-button @click="$alert(lorem(10), 'Base')">Base</fm-button>
      <fm-button type="info" @click="$alert.info(lorem(10), 'Info')">Info</fm-button>
      <fm-button type="warning" @click="$alert.warning(lorem(10), 'Warning')">Warning</fm-button>
      <fm-button type="error" @click="$alert.error(lorem(10), 'Error')">Error</fm-button>
      <fm-button type="success" @click="$alert.success(lorem(10), 'Success')">Success</fm-button>
    </div>

    <h2 class="text-xl font-title font-bold mt-6">Confirm service</h2>
    <div class="mt-3">
      <fm-button @click="$confirm(lorem(10), 'Base')">Base</fm-button>
      <fm-button type="info" @click="$confirm.info(lorem(10), 'Info')">Info</fm-button>
      <fm-button type="warning" @click="$confirm.warning(lorem(10), 'Warning')">Warning</fm-button>
      <fm-button type="error" @click="$confirm.error(lorem(10), 'Error')">Error</fm-button>
      <fm-button type="success" @click="$confirm.success(lorem(10), 'Success')">Success</fm-button>
    </div>

    <fm-dialog v-model="misc.dialog.isVisible">
      <template #header>Create a tier</template>
      {{ lorem(400) }}
      <template #footer>
        <div class="text-right">
          <fm-button @click="misc.dialog.isVisible = false;">Cancel</fm-button>
          <fm-button type="primary" @click="misc.dialog.isVisible = false;">Submit</fm-button>
        </div>
      </template>
    </fm-dialog>
  </section>
  <!-- dialogs end -->

  <!-- card start -->
  <section v-show="sections.card" class="pb-12 mb-12 border-b-2">
    <h2 class="text-3xl font-title font-bold mb-6">Card</h2>

    <div class="row g-4">
      <div v-for="i in 3" :key="i" class="col-12 sm:col-6 lg:col">
        <fm-card>
          <template #header>
            Good night Hulkamaniacs
          </template>
          {{ lorem(30) }}
        </fm-card>
      </div>
    </div>
  </section>
  <!-- card end -->

</section>
</template>

<script>
const LOREM = 'Lorem ipsum dolor sit amet consectetur, adipisicing elit. Reiciendis ipsam quae rem voluptatum, vitae, et mollitia officiis magni provident reprehenderit qui adipisci itaque quisquam, ea voluptates molestias culpa. Quibusdam laboriosam culpa reiciendis saepe facere dolorum, sapiente esse, ut modi architecto temporibus exercitationem earum cupiditate? Molestias voluptas dolorum vitae harum incidunt itaque et maiores minus. Laboriosam explicabo neque vel aliquid at, libero quos harum autem pariatur repudiandae molestias? Tenetur sint temporibus sit eaque minus? Ducimus, doloribus natus repellendus quam quibusdam voluptatibus, animi ipsam doloremque fuga assumenda deleniti dolorem maiores officia obcaecati labore voluptates alias quas mollitia debitis. Doloremque, molestias perferendis debitis doloribus ex nihil sint aperiam pariatur dolor culpa nesciunt, rem accusantium illo nulla sit architecto eaque saepe placeat, amet deserunt enim. Minus, error? Natus reprehenderit, numquam, sit aspernatur repudiandae cupiditate nobis, earum nemo dolor voluptatum perferendis quisquam a! Sequi, blanditiis ea voluptatem eaque laborum aperiam eos aut? Quod maiores sed dolores corrupti explicabo accusantium, minus iusto eum eligendi error neque quis officia culpa esse dolorem, hic reiciendis eius! Nulla eligendi tempore consequuntur recusandae placeat consequatur! Necessitatibus est atque sunt ipsam illo unde alias nisi reprehenderit ullam, error possimus repudiandae asperiores quis minus voluptatum ut fugiat! Repellat tempore veniam pariatur ex beatae optio, velit sint explicabo modi facilis repudiandae minus voluptate quam fugit, iste itaque! Assumenda dolore, magni repellat ea quod nam debitis explicabo obcaecati nihil eaque, animi voluptate provident delectus accusantium odit aliquid, molestiae itaque? Laboriosam neque distinctio ullam quod voluptatibus possimus provident odio officia ipsa vel nihil voluptate sint, odit perferendis cum ipsum aliquid ut. Facere repudiandae quae aspernatur praesentium voluptates exercitationem nam, earum quidem architecto quam blanditiis ex corrupti distinctio nemo ab, ducimus eum rem maiores dicta tempore culpa ipsam eligendi ullam officiis. Esse, distinctio commodi? Recusandae voluptate veniam officia quas voluptates repudiandae provident facilis est aut consectetur excepturi doloribus beatae laudantium minima quisquam et sunt, impedit eaque reiciendis! Nemo dolore magni consectetur eos dignissimos. Expedita rem, accusantium blanditiis sint obcaecati praesentium nam sed ipsa reiciendis cumque tempore molestiae, laborum quisquam perspiciatis nobis voluptates laboriosam voluptatum maiores doloremque ea temporibus minus ab. Obcaecati, hic ducimus debitis amet quidem molestias illum dolor est libero, ut minima. Magnam, sed nam rerum asperiores provident aperiam fugiat enim rem deleniti recusandae veniam dolorum maiores, aspernatur nobis? Accusamus quos ipsum animi labore non esse voluptas saepe laboriosam ea dolor doloribus sapiente dignissimos at eos optio perspiciatis veritatis reiciendis, minus molestiae hic amet corrupti quisquam. Unde dolores eaque eveniet molestiae totam, accusamus aspernatur nihil error at nisi repudiandae tempore fugit similique distinctio libero, inventore vel perferendis reiciendis et suscipit voluptates culpa. Officiis ab, repellendus facere repudiandae quam fugit reiciendis voluptatum animi quas aperiam cumque quis minus similique magni, ullam deleniti aliquid? Corporis, eius vitae sapiente eveniet assumenda numquam vel consectetur itaque temporibus, odio sit officiis, quidem quos quasi facere repellat autem error quam quia voluptatem impedit dolorem consequuntur voluptate id! Odio vel nobis minus dolorum error, doloremque maxime ipsa at modi enim non consequatur fugiat repellendus possimus odit, cumque, consectetur ratione exercitationem? In, esse?';

export default {
  auth: false,
  data() {
    return {
      model: '',
      lorem: (words = 20) => LOREM.split(' ').slice(0, words).join(' '),
      sections: {
        button: false,
        input: false,
        alert: false,
        wizard: false,
        dialog: true,
        card: false
      },
      misc: {
        alert: {
          clamped: false
        },
        wizard: {
          current: 2
        },
        dialog: {
          isVisible: false
        }
      }
    };
  },
  computed: {
    sectionAll: {
      get() {
        return Object.values(this.sections).every(v => !!v);
      },
      set(val) {
        Object.keys(this.sections).forEach(key => {
          this.sections[key] = val;
        });
      }
    }
  }
};
</script>
