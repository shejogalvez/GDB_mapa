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
        <v-select label="Comparison" :disabled="isFilterApplied" v-model="operation_key" density="compact" variant="outlined"
            :items="Object.keys(operation_map)">
        </v-select>
        
        <!-- Text Input -->
        <v-text-field 
            label="Value" 
            :disabled="isFilterApplied" 
            v-model="val" density="compact" 
            variant="outlined" 
            v-if="!['is_empty', 'is_not_empty'].includes(operation_key)"
        />
        
        <!-- Apply Filters Button -->
        <v-btn @click="applyFilters">{{isFilterApplied ? 'Remove Filters': 'Apply Filters' }}</v-btn>
      </div>
    </th>
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
            operation_map: {
                equals: '=',
                contains: 'contains',
                less_than: '<',
                more_then: '>',
                is_empty: 'is null',
                is_not_empty: 'is not null',
            },
            operation_key: '',
            store: useFilterStore()
        }
    },
    methods: {
        applyFilters() {
            const store = this.store
            if (!this.isFilterApplied) {
                const filterObj = {
                    key: this.property_label,
                    operation: this.operation_map[this.operation_key],
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
                this.reset();
            }
            this.$emit('applyFilter');
            this.isOpen = false;
        },
        openMenu() {
            this.isOpen = !this.isOpen;
        },
        reset() {
            this.isOpen= false;
            this.val= '';
            this.operation_key= '';
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
    padding: 15pt 15pt 0pt 15pt ;
    z-index: 2;
}
.filter-menu label {
    border-color: black;
    border: 5pt;
}
.v-text-field{
    height: 30pt;
}
</style>