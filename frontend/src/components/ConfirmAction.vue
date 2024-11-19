<template>
    <div>
      <div @click="open=true" style="display: inline-block;">
        <slot></slot>
      </div>
      <v-dialog
        v-model="open"
        max-width="400"
        persistent
      >
        <v-card
          :text="text"
          :title="title"
        >
          <template v-slot:actions>
            <v-spacer></v-spacer>
  
            <v-btn @click="open = false">
              Cancelar
            </v-btn>
  
            <v-btn :type="btnType" color="blue" @click="confirmFunction">
              Confirmar
            </v-btn>
          </template>
        </v-card>
      </v-dialog>
    </div>
  </template>

<script>
export default {
    props: {
        text: {
            type: String
        },
        title: {
            type: String
        },
        btnType: {
          type: String,
          default: "submit",
        },
        confirmFunction: {
            type: Function
        }
    },
    data() {
        return {open: false}
    }
}
</script>