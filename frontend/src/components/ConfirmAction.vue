<template>
    <div>
      <v-dialog
        v-model="open"
        max-width="400"
        persistent
      >
        <template v-slot:activator="{ props: activatorProps }">
          <v-btn color="blue" v-bind="activatorProps">
            {{ buttonText }}
          </v-btn>
        </template>
  
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
        buttonText: {
            type: String,
            default: "Enviar"
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