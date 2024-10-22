<template>
    <div class="custom-select" :tabindex="tabindex" @blur="open = false">
        <div class="selected" :class="{ open: open }" @click="open = !open">
        {{ selected.name }}
        </div>
        <div class="items" :class="{ selectHide: !open }">
            <DropdownItem
                v-for="option of options"
                :item="option"
                :children_key="children_key"
                @input="(item) => {selected = item; open = false; $emit('input', item)}"
            >
            </DropdownItem>
        </div>
    </div>
</template>

<script>
import DropdownItem from './DropdownItem.vue';

export default {
    components:{
        DropdownItem
    },
  props: {
    options: {
      type: Array,
      required: true,
    },
    default: {
      type: String,
      required: false,
      default: null,
    },
    tabindex: {
      type: Number,
      required: false,
      default: 0,
    },
    children_key: {
      type: String,
      required: false,
      default: 'children',
    },
  },
  data() {
    return {
      selected: this.default
        ? this.default
        : this.options.length > 0
        ? this.options[0]
        : null,
      open: false,
    };
  },
  mounted() {
    this.$emit("input", this.selected);
    console.log(this.selected.name);
  },
};
</script>

<style>

.custom-select {
  position: relative;
  width: 100%;
  text-align: left;
  outline: none;
  height: 20px;
  line-height: 47px;
}

.custom-select .selected {
  border-radius: 6px;
  border: 1px solid #666666;
  padding-left: 1em;
  cursor: pointer;
  user-select: none;
}

.custom-select .selected.open {
  border: 1px solid #ad8225;
  border-radius: 6px 6px 0px 0px;
}

.custom-select .selected:after {
  position: absolute;
  content: "";
  top: 22px;
  right: 1em;
  width: 0;
  height: 0;
  border-color: #000000;
}

.custom-select .items {
  border-radius: 0px 0px 6px 6px;
  overflow: hidden;
  border-right: 1px solid #ad8225;
  border-left: 1px solid #ad8225;
  border-bottom: 1px solid #ad8225;
  position: absolute;
  left: 0;
  right: 0;
  z-index: 1;
}

.selectHide {
  display: none;
}
</style>