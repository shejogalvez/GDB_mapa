<template>
    <th>{{header_text}} <v-btn
        @click = "openMenu"
        class="ma-2"
        :color="isFilterApplied ? 'green' : 'blue-lighten-2'"
        :icon= "isOpen ? 'mdi-filter-menu' : 'mdi-filter-menu-outline'"
        variant="text"  
      ></v-btn>
      
      <div v-if="isOpen" class="filter-menu">
        <!-- Select Comparison Option -->
        <label>
            Comparison:
            <select v-model="operation">
                <option value="=">Equals</option>
                <option value="contains">Contains</option>
                <option value="<">Is Less Than</option>
                <option value=">">Is Greater Than</option>
            </select>
        </label>
        
        <!-- Text Input -->
        <label>
            Value:
            <input type="text" v-model="val" />
        </label>
        
        <!-- Apply Filters Button -->
        <v-btn @click="applyFilters">{{isFilterApplied ? 'Remove Filters': 'Apply Filters' }}</v-btn>
      </div></th>
</template>

<script>
import { useFilterStore } from '@/stores/store';
export default  {
    props: {
        header_text: {
            type: String,
            required: true
        },
        node_label: {
            type: String,
            required: false,
            default: 'pieza'
        },
        property_label: {
            type: String,
            required: true
        }
    },
    data() {
        return {
            isOpen: false,
            val: '',
            operation: '',
            store: useFilterStore()
        }
    },
    methods: {
        applyFilters() {
            const store = this.store
            if (!this.isFilterApplied) {
                const filterObj = {
                    key: this.property_label,
                    operation: this.operation,
                    val: this.val
                }
                store.$patch((state) => {
                    state.filters[this.node_label].push(filterObj);
                })
            }
            else {
                store.$patch((state) => {
                    state.filters[this.node_label] = state.filters[this.node_label].filter((filter) => filter.key != this.property_label);
                })
            }
            this.$emit('applyFilter');
            this.reset()
        },
        openMenu() {
            this.isOpen = !this.isOpen;
        },
        reset() {
            this.isOpen= false;
            this.val= '';
            this.operation= '';
        }
    },
    computed: {
        isFilterApplied() {
            return Boolean(this.store.$state.filters[this.node_label].find((filter) => filter.key === this.property_label))
        },
    },
}
</script>

<style scoped>
th {
    position: relative;
}

.filter-menu {
    position: absolute;
    width: 250pt;
    height: 150pt;
    display: grid;
    background-color: white;
    z-index: 2;
}
.filter-menu label {
    border-color: black;
    border: 5pt;
}
</style>