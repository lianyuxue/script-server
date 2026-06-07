<template>
  <div ref="parametersPanel" :style="{ 'grid-template-columns': 'repeat(' + gridColumns + ', minmax(0, 1fr))'}"
       class="script-parameters-panel">
    <div v-for="item in flattenedItems"
         :key="item.id"
         :class="item.isSeparator ? 'separator-container' : paramItemClasses(item)"
         :style="item.isSeparator ? { gridColumn: '1 / span ' + gridColumns } : getGridCellStyle(item)">
      <ParameterSeparator v-if="item.isSeparator" :separator="item.separator"/>
      <div v-else class="param-row">
        <div class="param-label-col">
          <span class="param-label">{{ item.name }}</span>
          <span v-if="item.required" class="param-tag">必填</span>
          <span v-if="item.description" class="param-help">
            <i class="material-icons">help_outline</i>
            <span class="param-tooltip">{{ item.description }}</span>
          </span>
        </div>
        <div :class="paramValueClasses(item)"
             class="param-value-col">
          <div v-if="!item.withoutValue"
               :class="'param-input-wrap type-' + getFieldTypeClass(item)">
            <span v-if="useWrapIcon(item)" class="param-input-icon">
              <i class="material-icons">{{ getFieldIcon(item) }}</i>
            </span>
            <component
                :is="getComponentType(item)"
                :config="getControlConfig(item)"
                :value="getParameterValue(item)"
                :dropdownContainer="dropdownContainer"
                class="parameter param-control"
                :forceValue="forcedValueParameters.includes(item.name)"
                @error="handleError(item, $event)"
                @input="setParameterValue(item.name, $event)"/>
            <span v-if="hasValue(item)"
                  class="param-input-clear"
                  title="清空内容"
                  @click="clearParameterValue(item)">
              <i class="material-icons">close</i>
            </span>
          </div>
          <component
              v-else
              :is="getComponentType(item)"
              :config="getControlConfig(item)"
              :value="getParameterValue(item)"
              class="parameter param-control"
              :forceValue="forcedValueParameters.includes(item.name)"
              @error="handleError(item, $event)"
              @input="setParameterValue(item.name, $event)"/>
        </div>
      </div>
      <p v-if="!item.isSeparator && parameterErrors[item.name]" class="param-error">
        <i class="material-icons">info</i>
        {{ formatError(parameterErrors[item.name]) }}
      </p>
    </div>
  </div>
</template>

<script>
import Checkbox from '@/common/components/checkbox'
import Combobox from '@/common/components/combobox'
import FileUpload from '@/common/components/file_upload'
import ServerFileField from '@/common/components/server_file_field'
import TextArea from '@/common/components/TextArea'
import Textfield from '@/common/components/textfield'
import {isNull} from '@/common/utils/common';
import ParameterSeparator from '@/main-app/components/scripts/ParameterSeparator.vue';
import {mapActions, mapState} from 'vuex'
import {comboboxTypes, isRecursiveFileParameter} from '../../utils/model_helper'

const ERROR_MESSAGES = {
  required: '此项为必填',
  'integer expected': '请输入整数',
  'IPv4 or IPv6 expected': '请输入有效的 IP 地址',
  'IPv4 expected': '请输入有效的 IPv4 地址'
};

export default {
  name: 'script-parameters-view',
  components: {ParameterSeparator},

  data: function () {
    return {
      gridColumns: 7,
      dropdownContainer: null
    }
  },

  computed: {
    ...mapState('scriptConfig', {
      parameters: 'parameters'
    }),
    ...mapState('scriptSetup', {
      parameterValues: 'parameterValues',
      forcedValueParameters: 'forcedValueParameters',
      parameterErrors: 'errors'
    }),

    flattenedItems() {
      const items = [];
      this.parameters.forEach(p => {
        if (p.ui && p.ui.separatorBefore) {
          items.push({
            id: 'sep-' + p.name,
            isSeparator: true,
            separator: p.ui.separatorBefore
          });
        }
        items.push({
          ...p,
          id: p.name,
          isSeparator: false
        });
      });
      return items;
    }
  },

  mounted() {
    this.dropdownContainer = document.body
    window.addEventListener('resize', this.recalculateParamsLayout)

    this.$nextTick(() => {
      this.recalculateParamsLayout()
    })
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.recalculateParamsLayout)
  },

  methods: {
    ...mapActions('scriptSetup', {
      setParameterValueInStore: 'setParameterValue',
      setParameterErrorInStore: 'setParameterError'
    }),

    formatError(error) {
      return ERROR_MESSAGES[error] || error;
    },

    paramItemClasses(parameter) {
      return {
        'param-item': true,
        'param-item-chip': parameter.withoutValue,
        'param-item-wide': !this.isInline(parameter),
        'has-error': !!this.parameterErrors[parameter.name]
      };
    },

    paramValueClasses(parameter) {
      return {
        'param-value-wide': !this.isInline(parameter),
        'param-value-toggle': parameter.withoutValue,
        ['param-type-' + this.getFieldTypeClass(parameter)]: !parameter.withoutValue
      };
    },

    getFieldTypeClass(parameter) {
      if (parameter.type === 'file_upload') return 'file';
      if (isRecursiveFileParameter(parameter)) return 'server-file';
      if (comboboxTypes.includes(parameter.type)) return 'select';
      if (parameter.type === 'multiline_text') return 'text';
      if (this.isNumberParameter(parameter)) return 'int';
      if (parameter.secure) return 'secure';
      if (parameter.type === 'ip' || parameter.type === 'ip4' || parameter.type === 'ip6') return 'ip';
      return 'default';
    },

    isNumberParameter(parameter) {
      return parameter.type === 'int'
          || parameter.type === 'integer'
          || parameter.type === 'number';
    },

    getFieldIcon(parameter) {
      if (parameter.type === 'file_upload') return 'file_upload';
      if (isRecursiveFileParameter(parameter)) return 'folder_open';
      if (comboboxTypes.includes(parameter.type)) return 'arrow_drop_down';
      if (parameter.type === 'multiline_text') return 'notes';
      if (this.isNumberParameter(parameter)) return 'plus_one';
      if (parameter.secure) return 'lock_outline';
      if (parameter.type === 'ip' || parameter.type === 'ip4' || parameter.type === 'ip6') return 'language';
      return 'edit';
    },

    useWrapIcon(parameter) {
      const icon = this.getFieldIcon(parameter);
      if (!icon) return false;

      return !isRecursiveFileParameter(parameter);
    },

    getControlConfig(parameter) {
      return Object.assign({}, parameter, {description: null});
    },

    getComponentType(parameter) {
      if (parameter.withoutValue) {
        return Checkbox;
      } else if (isRecursiveFileParameter(parameter)) {
        return ServerFileField;
      } else if (comboboxTypes.includes(parameter.type)) {
        return Combobox;
      } else if (parameter.type === 'file_upload') {
        return FileUpload;
      } else if (parameter.type === 'multiline_text') {
        return TextArea;
      } else {
        return Textfield;
      }
    },

    isInline(parameter) {
      return parameter.type !== 'multiline_text'
    },

    handleError(parameter, error) {
      this.setParameterErrorInStore({parameterName: parameter.name, errorMessage: error})
    },

    setParameterValue(parameterName, value) {
      this.setParameterValueInStore({parameterName, value});
    },

    clearParameterValue(parameter) {
      this.setParameterValue(parameter.name, null);
    },

    hasValue(parameter) {
      const value = this.parameterValues[parameter.name];
      return !isNull(value) && value !== '' && value !== false;
    },

    getParameterValue(parameter) {
      const value = this.parameterValues[parameter.name];
      if (!isNull(value)) {
        return value;
      }

      if (parameter.withoutValue) {
        return false;
      }

      return value;
    },

    recalculateParamsLayout() {
      const width = this.$refs.parametersPanel.clientWidth
      const minCellWidth = 200

      this.gridColumns = Math.max(1, Math.floor(width / minCellWidth))
    },

    getGridCellStyle(parameter) {
      if (this.isInline(parameter)) {
        const styles = []

        if (this.startsWithNewLine(parameter)) {
          styles.push('grid-column-start: 1')
        }

        let widthWeight = parameter.ui?.['widthWeight'];
        if (widthWeight) {
          styles.push('grid-column-end: span ' + Math.min(widthWeight, this.gridColumns))
        }

        return styles.join('; ')
      }

      return 'grid-column-end: span ' + this.gridColumns
    },

    startsWithNewLine(parameter) {
      const separator = parameter.ui?.separatorBefore
      if (isNull(separator)) {
        return false
      }

      if (separator.title) {
        return false
      }

      return separator.type === 'new_line'
    }
  }
}
</script>

<style scoped>
.script-parameters-panel {
  margin: 0;
  padding: 10px 12px 14px;
  display: grid;
  gap: 12px;
  align-items: stretch;
}

.separator-container {
  grid-column: 1 / -1;
  margin: 1.2rem 0 0.8rem;
  padding: 0 10px;
}

.param-item {
  min-width: 0;
  padding: 4px 0;
}

.param-row {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
  min-height: 34px;
}

.param-item-wide .param-row {
  align-items: flex-start;
}

.param-label-col {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 0 0 auto;
  max-width: 34%;
  min-width: 0;
}

.param-item-wide .param-label-col {
  padding-top: 6px;
}

.param-label {
  min-width: 0;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--font-color-main);
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.param-help {
  position: relative;
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid var(--separator-color);
  color: var(--font-color-medium);
  cursor: help;
}

.param-help .material-icons {
  font-size: 0.82rem;
}

.param-help .param-tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  top: calc(100% + 8px);
  left: -8px;
  z-index: 30;
  min-width: 160px;
  max-width: 260px;
  padding: 7px 10px;
  border-radius: 6px;
  border: 1px solid var(--separator-color);
  background: var(--background-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-size: 0.72rem;
  font-weight: 400;
  line-height: 1.45;
  color: var(--font-color-medium);
  white-space: normal;
  text-align: left;
  pointer-events: none;
  transition: opacity 0.15s ease, visibility 0.15s ease;
}

.param-help .param-tooltip::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 16px;
  margin-left: -5px;
  border: 5px solid transparent;
  border-bottom-color: var(--separator-color);
}

.param-help .param-tooltip::after {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 16px;
  margin-left: -4px;
  border: 4px solid transparent;
  border-bottom-color: var(--background-color);
}

.param-help:hover .param-tooltip {
  visibility: visible;
  opacity: 1;
}

.param-value-col {
  flex: 1 1 0;
  min-width: 0;
  display: flex;
  align-items: center;
}

.param-value-toggle {
  justify-content: flex-end;
}

.param-value-wide {
  width: 100%;
}

.param-tag {
  flex-shrink: 0;
  padding: 0 4px;
  border-radius: 3px;
  font-size: 0.58rem;
  font-weight: 600;
  line-height: 1.35;
  color: #e65100;
  border: 1px solid rgba(255, 152, 0, 0.25);
}

.param-error {
  display: flex;
  align-items: center;
  gap: 3px;
  margin: 2px 0 0;
  font-size: 0.68rem;
  line-height: 1.3;
  color: #c62828;
}

.param-error .material-icons {
  font-size: 0.82rem;
}

.script-parameters-panel >>> .param-item-chip .param-control.checkbox {
  display: flex;
  align-items: center;
  margin: 0;
  padding: 0;
  cursor: pointer;
}

.script-parameters-panel >>> .param-control.input-field {
  margin: 0;
  padding: 0;
}

.script-parameters-panel >>> .param-control.input-field:before,
.script-parameters-panel >>> .param-control.input-field:after {
  display: none !important;
}

.script-parameters-panel >>> .param-control.input-field > label,
.script-parameters-panel >>> .param-control .file-upload-field-label {
  display: none !important;
}

.script-parameters-panel >>> .param-item-chip .param-control.checkbox input[type=checkbox] + span {
  display: none;
}

/* ── 统一输入框容器 ── */

.param-input-wrap {
  display: flex;
  align-items: center;
  width: 100%;
  min-height: 32px;
  border: 1px solid var(--separator-color);
  border-radius: 6px;
  background: var(--background-color);
  overflow: visible;
  transition: border-color 0.12s ease;
}

.param-input-wrap.type-select {
  position: relative;
  z-index: 1;
}

.param-item:focus-within .param-input-wrap.type-select,
.param-input-wrap.type-select:focus-within {
  z-index: 10;
}

.param-input-wrap:focus-within {
  border-color: var(--primary-color);
}

.param-item.has-error .param-input-wrap {
  border-color: #ef5350;
}

.param-input-wrap.type-text {
  align-items: stretch;
  min-height: 64px;
}

.param-input-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  align-self: stretch;
  border-right: 1px solid var(--separator-color);
  color: var(--font-color-medium);
  background: rgba(0, 0, 0, 0.02);
}

.param-input-wrap.type-text .param-input-icon {
  padding-top: 6px;
  align-items: flex-start;
}

.param-input-icon .material-icons {
  font-size: 1rem;
}

.param-input-clear {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  margin-right: 4px;
  border-radius: 50%;
  color: var(--font-color-disabled);
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.15s ease;
}

.param-input-clear:hover {
  opacity: 1;
  color: #ef5350;
  background: rgba(239, 83, 80, 0.08);
}

.param-input-clear .material-icons {
  font-size: 1.1rem;
}

.param-input-wrap >>> .param-control {
  flex: 1 1 0;
  min-width: 0;
}

/* ── 控件样式 ── */

.script-parameters-panel >>> .param-control {
  width: 100%;
}

.script-parameters-panel >>> .param-input-wrap .param-control input:not([type=checkbox]):not([type=file]):not(.select-dropdown),
.script-parameters-panel >>> .param-input-wrap .param-control textarea,
.script-parameters-panel >>> .param-input-wrap .param-control .select-wrapper input.select-dropdown,
.script-parameters-panel >>> .param-input-wrap .param-control .file-upload-field-value,
.script-parameters-panel >>> .param-input-wrap .param-control.server-file-field input {
  display: block;
  width: 100%;
  margin: 0;
  font-size: 0.82rem;
  color: var(--font-color-main);
  background: transparent;
  border: none;
  border-radius: 0;
  box-sizing: border-box;
  outline: none;
}

.script-parameters-panel >>> .param-input-wrap .param-control input:not([type=checkbox]):not([type=file]):not(.select-dropdown),
.script-parameters-panel >>> .param-input-wrap .param-control .select-wrapper input.select-dropdown,
.script-parameters-panel >>> .param-input-wrap .param-control .file-upload-field-value,
.script-parameters-panel >>> .param-input-wrap .param-control.server-file-field input {
  padding: 0 10px;
  height: 32px;
  line-height: 32px;
}

.script-parameters-panel >>> .param-input-wrap.type-int .param-control input[type=number] {
  -moz-appearance: textfield;
}

.script-parameters-panel >>> .param-input-wrap.type-int .param-control input[type=number]::-webkit-inner-spin-button,
.script-parameters-panel >>> .param-input-wrap.type-int .param-control input[type=number]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.script-parameters-panel >>> .param-input-wrap .param-control textarea {
  padding: 6px 10px;
  min-height: 62px;
  line-height: 1.45;
  resize: vertical;
}

.script-parameters-panel >>> .param-input-wrap .param-control input:focus,
.script-parameters-panel >>> .param-input-wrap .param-control textarea:focus,
.script-parameters-panel >>> .param-input-wrap .param-control .select-wrapper input.select-dropdown:focus {
  border-color: transparent;
}

.script-parameters-panel >>> .param-input-wrap .param-control.combobox .select-wrapper {
  width: 100%;
}

.script-parameters-panel >>> .param-input-wrap .param-control .select-wrapper input.select-dropdown {
  padding-right: 28px;
}

.script-parameters-panel >>> .param-input-wrap .param-control .select-wrapper .caret {
  right: 8px;
  fill: var(--font-color-medium);
}

.script-parameters-panel >>> .param-input-wrap .param-control.combobox .loading-spinner {
  top: 7px;
  right: 26px;
}

/* 文件上传：左侧图标按钮 */

.script-parameters-panel >>> .param-type-file .file-upload-field {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
}

.script-parameters-panel >>> .param-type-file .file-upload-field input[type=file] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.script-parameters-panel >>> .param-type-file .file-upload-field .btn-icon-flat {
  order: -1;
  position: static;
  transform: none;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin: 0;
  padding: 0;
  border-right: 1px solid var(--separator-color);
  border-radius: 0;
  background: rgba(0, 0, 0, 0.02);
  color: var(--font-color-medium);
  box-shadow: none;
}

.script-parameters-panel >>> .param-type-file .file-upload-field .btn-icon-flat:hover {
  color: var(--primary-color);
  background: rgba(38, 166, 154, 0.06);
}

.script-parameters-panel >>> .param-type-file .file-upload-field .btn-icon-flat .material-icons {
  font-size: 1rem;
  clip-path: none;
}

.script-parameters-panel >>> .param-type-file .file-upload-field .file-upload-field-value {
  flex: 1;
  min-width: 0;
  padding: 0 10px;
  cursor: pointer;
}

.script-parameters-panel >>> .param-type-file .file-upload-field .file-upload-field-value:empty::before {
  content: '选择文件…';
  color: var(--font-color-disabled);
}

/* 服务器文件：左侧文件夹图标 */

.script-parameters-panel >>> .param-type-server-file .server-file-field {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
}

.script-parameters-panel >>> .param-type-server-file .server-file-field .btn-icon-flat {
  order: -1;
  position: static;
  transform: none;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin: 0;
  padding: 0;
  border-right: 1px solid var(--separator-color);
  border-radius: 0;
  background: rgba(0, 0, 0, 0.02);
  color: var(--font-color-medium);
}

.script-parameters-panel >>> .param-type-server-file .server-file-field .btn-icon-flat:hover {
  color: var(--primary-color);
  background: rgba(38, 166, 154, 0.06);
}

.script-parameters-panel >>> .param-type-server-file .server-file-field .btn-icon-flat .material-icons {
  font-size: 1rem;
}

.script-parameters-panel >>> .param-type-server-file .server-file-field input {
  flex: 1;
  min-width: 0;
  padding: 0 10px;
  cursor: pointer;
  border-bottom: none !important;
  box-shadow: none !important;
}

.script-parameters-panel >>> .param-type-server-file .server-file-field input:focus {
  border-bottom: none !important;
  box-shadow: none !important;
}

/* 复选框 */

.script-parameters-panel >>> .param-item-chip .param-control input[type=checkbox] {
  position: relative;
  width: 38px;
  height: 20px;
  margin: 0;
  appearance: none;
  background: var(--separator-color);
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s ease;
  flex-shrink: 0;
}

.script-parameters-panel >>> .param-item-chip .param-control input[type=checkbox]::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  transition: transform 0.15s ease, background 0.15s ease;
}

.script-parameters-panel >>> .param-item-chip .param-control input[type=checkbox]:checked {
  background: #e8a317;
}

.script-parameters-panel >>> .param-item-chip .param-control input[type=checkbox]:checked::before {
  transform: translateX(18px);
  background: #2c2c2c;
  box-shadow: none;
}

.script-parameters-panel >>> .dropdown-content {
  border-radius: 6px;
  border: 1px solid var(--separator-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  max-width: min(480px, 90vw);
  min-width: 100%;
  max-height: 280px;
  overflow-y: auto;
  margin-top: 4px;
}

.script-parameters-panel >>> .dropdown-content > li > span {
  font-size: 0.82rem;
  padding: 8px 12px;
}

.script-parameters-panel >>> .dropdown-content li:hover {
  background: rgba(0, 0, 0, 0.04);
}

.script-parameters-panel >>> .dropdown-content li.selected,
.script-parameters-panel >>> .dropdown-content li.selected:hover {
  background: rgba(232, 163, 23, 0.18);
}

.script-parameters-panel >>> .dropdown-content li.selected > span {
  color: var(--font-color-main);
  font-weight: 500;
}

</style>
