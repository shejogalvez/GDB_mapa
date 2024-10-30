import { defineStore } from "pinia";

export const useStore = defineStore('store', {
    state: () => ({
        emptyPiece: {
            id: "",
            pieza: {},
            pais: null,
            localidad: null,
            cultura: null,
            components: []
        }, 
        currentPiece: null,
        filters: {
            pieza: [],
            pais: [],
            localidad: [],
            cultura: [],
            exposicion: [],
        }
    })
    
})