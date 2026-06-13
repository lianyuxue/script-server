<template>
  <div :data-error="error" :title="config.description" class="input-field file-upload-field">
    <div class="file-upload-content" @click="triggerUpload">
      <span class="file-upload-value" :class="{ 'has-file': valueText }">{{ valueText || '点击选择文件...' }}</span>
    </div>
    <input :id="config.name"
           ref="fileField"
           :required="config.required"
           class="validate"
           type="file"
           @blur="focused = false"
           @change="updateValue"
           @focus="focused = true"/>
    <label :for="config.name" class="file-upload-field-label" v-bind:class="{ active: (value || focused) }">
      {{ config.name }}</label>
  </div>
</template>

<script>
import {getFileInputValue, isNull} from '@/common/utils/common';

export default {
  props: {
    'value': [File],
    'config': Object
  },

  data: function () {
    return {
      error: '',
      focused: false
    }
  },

  computed: {
    valueText() {
      if (isNull(this.value)) {
        return '';
      }

      return this.value.name;
    },
  },

  mounted: function () {
    this.updateValue();
  },

  methods: {
    triggerUpload() {
      this.$refs.fileField.click();
    },

    updateValue() {
      const fileField = this.$refs.fileField;
      let value = getFileInputValue(fileField)

      this.error = this.getValidationError(value);
      fileField.setCustomValidity(this.error);

      this.$emit('error', this.error);
      this.$emit('input', value);
    },

    getValidationError(value) {
      var empty = isNull(value);

      if (this.config.required && empty) {
        return 'required';
      }

      return '';
    }
  }
}
</script>

<style scoped>
input[type=file] {
  position: absolute;
  left: -9999px;
  opacity: 0;
}

.file-upload-content {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  height: 32px;
  padding: 0 10px;
  box-sizing: border-box;
  cursor: pointer;
}

.file-upload-value {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-size: 0.82rem;
  color: var(--font-color-medium);
}

.file-upload-value.has-file {
  color: var(--font-color-main);
  font-weight: 500;
}

label {
  display: none;
}
</style>