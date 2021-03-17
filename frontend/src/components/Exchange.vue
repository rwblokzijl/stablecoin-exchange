<template>
  <v-container>
    <v-row justify="center">

      <v-col cols="3">
        <InfoBox title="Euro -> EuroToken" text="1.00 -> 1.00" icon="mdi-plus" color="green"/>
      </v-col>

      <v-col cols="3">
        <InfoBox title="EuroToken -> Euro" text="1.00 -> 1.00" icon="mdi-minus" color="red"/>
      </v-col>

    </v-row>
    <v-row class="text-center">
      <v-col cols="3" class="mb-4">
        <p>test</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

import InfoBox from '@/components/InfoBox';

  export default {
    name: 'Exchange',
    components: {
      InfoBox
    },

    data: () => ({

    }),
  }
</script>
