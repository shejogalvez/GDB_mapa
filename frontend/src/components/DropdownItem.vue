<template>
    <div class="flex-box">
        <div class="option" @click="$emit('input', item);">
        {{ item.name }}
        </div>
        <div v-if="hasChildren" @click="showChildren=!showChildren" class="dropdown-arrow"> &#x25BC </div>
    </div>
    <div class="ml-4" :class="{ selectHide: !showChildren }" v-if="hasChildren">
        <DropdownItem
            v-for="option of item[children_key]"
            :item="option"
            :children_key="children_key"
            @input="(child_item) => $emit('input', child_item)"
        >
        </DropdownItem>
    </div>
</template>

<script>
export default {
    emits: ['input'],
  props: {
    item: {
        type: Object,
        required: true
    },
    children_key: {
        type: String,
        required: true
    }
  },
  data() {
    return {
        showChildren: false
    };
  },
  computed: {
    hasChildren() {return this.item[this.children_key]?.length}
  },
  mounted() {
    //console.log(item);
  },
};
</script>

<style>
.ml-4{
    margin-left: 2rem;
}
.option {
  padding: 0em 1em;
  display: table-row;
  cursor: pointer;
  width: 90%;
}

.option:hover {
  background-color: #6f6f6f;
}

.flex-box {
    display: flex;
    flex-direction: row;
    width: 100%;
    align-items: justify;
}

.flex-box .dropdown-arrow{
    align-self: end;
    align-items: flex-end;
    margin-left: auto;
    padding: 0 3%;
    float: right;
}
.flex-box .dropdown-arrow:hover{
    background-color: #6f6f6f;
}
</style>