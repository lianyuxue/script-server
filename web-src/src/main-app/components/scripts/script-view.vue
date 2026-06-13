<template>
  <div :id="id" class="script-view">
    <ScriptLoadingText v-if="loading && !scriptConfig" :loading="loading" :script="selectedScript"/>

    <template v-else>
      <p v-show="scriptDescription" class="script-description" v-html="formattedDescription"/>

      <div class="script-workspace">
        <section v-show="!hideExecutionControls"
                 :class="{'config-collapsed': !parametersExpanded}"
                 class="config-zone">
          <div class="config-toolbar">
            <div class="toolbar-left">
              <button v-if="canCollapseParameters"
                      class="btn-flat collapse-toggle"
                      :title="parametersExpanded ? '收起参数' : '展开参数'"
                      @click="toggleParameters">
                <i class="material-icons">{{ parametersExpanded ? 'expand_less' : 'expand_more' }}</i>
              </button>
              <div v-if="parameterCount > 0" class="config-title">
                <span>参数配置</span>
                <span class="panel-badge">{{ parameterCount }}</span>
              </div>
              <div v-if="isExecuting" class="execution-status-inline">
                <span class="status-dot"></span>
                <span>运行中</span>
              </div>
            </div>
            <div class="toolbar-actions">
              <button v-show="!isExecuting"
                      :disabled="!enableExecuteButton || scheduleMode"
                      class="button-execute btn waves-effect"
                      v-bind:class="{ disabled: !enableExecuteButton || scheduleMode }"
                      @click="executeScript">
                <i class="material-icons">play_arrow</i>
                <span>Execute</span>
              </button>
              <button v-show="enableStopButton"
                      class="button-stop btn waves-effect"
                      v-bind:class="{ 'kill-mode': killEnabled }"
                      @click="stopScript">
                <i class="material-icons">{{ killEnabled ? 'close' : 'stop' }}</i>
                <span>{{ stopButtonLabel }}</span>
              </button>
              <ScheduleButton v-if="schedulable"
                              :disabled="!enableScheduleButton"
                              class="schedule-action"
                              @click="openSchedule"/>
            </div>
          </div>

          <div :class="{'is-collapsed': !parametersExpanded || parameterCount === 0}"
               class="config-body">
            <ScriptParametersView ref="parametersView"/>
            <div v-if="hasErrors" class="validation-panel">
              <div class="validation-panel-title">校验未通过</div>
              <ul class="validation-errors-list">
                <li v-for="error in shownErrors" :key="error">{{ error }}</li>
              </ul>
            </div>
          </div>

          <div v-if="!parametersExpanded && parameterCount > 0" class="config-collapsed-hint">
            已收起 {{ parameterCount }} 个参数，点击上方箭头展开
          </div>
        </section>

        <main class="output-panel">
          <div class="output-panel-body">
            <LogPanel v-show="showLog && !hasErrors && !hideExecutionControls"
                      ref="logPanel"
                      :outputFormat="outputFormat"
                      :inputPromptText="inputPromptText"
                      @user-input="handleUserInput"/>
            <LogPanel v-if="preloadOutput && !showLog && !hasErrors && !hideExecutionControls"
                      ref="preloadOutputPanel"
                      :output-format="preloadOutputFormat"/>
            <div v-if="!showLog && !preloadOutput && !hideExecutionControls"
                 class="output-placeholder">
              <i class="material-icons">play_circle_outline</i>
              <p>配置参数后点击 Execute 开始执行</p>
            </div>
          </div>

          <div v-if="downloadableFiles && (downloadableFiles.length > 0) && !scheduleMode"
               v-show="!hideExecutionControls"
               class="files-download-panel">
            <a v-for="file in downloadableFiles"
               :key="file.url"
               :download="file.filename"
               :href="file.url"
               class="waves-effect btn-flat"
               target="_blank">
              {{ file.filename }}
              <i class="material-icons right">file_download</i>
            </a>
          </div>

          <div v-if="inputPromptText"
               v-show="!hideExecutionControls"
               class="script-input-panel">
            <div class="input-outer-wrapper">
              <div class="input-wrapper linux-input-wrapper">
                <span class="linux-prompt">$</span>
                <input :id="'inputField-' + id"
                       ref="inputField"
                       class="script-input-field"
                       type="text"
                       @keydown.up.prevent="navigateHistory('up')"
                       @keydown.down.prevent="navigateHistory('down')"
                       @input="handleInputChange"
                       @keyup.enter="submitManualInput">
                <div class="action-buttons">
                   <button class="send-button waves-effect waves-light" @click="submitManualInput" title="发送 (Enter)">
                     <i class="material-icons">send</i>
                   </button>
                   <div class="divider-vertical"></div>
                   <a class="action-button waves-effect waves-circle" @click="copyLogToClipboard" title="复制日志">
                     <i class="material-icons">content_copy</i>
                   </a>
                   <a class="action-button waves-effect waves-circle" @click="downloadLog" title="下载日志">
                     <i class="material-icons">file_download</i>
                   </a>
                   <a class="action-button waves-effect waves-circle" @click="toggleFullscreen" title="全屏查看">
                     <i class="material-icons">fullscreen</i>
                   </a>
                 </div>
               </div>
             </div>
           </div>
        </main>
      </div>
    </template>

    <ScriptViewScheduleHolder v-if="!hideExecutionControls"
                              ref="scheduleHolder"
                              :scriptConfigComponentsHeight="scriptConfigComponentsHeight"
                              @close="scheduleMode = false"/>
  </div>
</template>

<script>

import LogPanel from '@/common/components/log_panel'
import {deepCloneObject, forEachKeyValue, isEmptyObject, isEmptyString, isNull} from '@/common/utils/common';
import ScheduleButton from '@/main-app/components/scripts/ScheduleButton';
import ScriptLoadingText from '@/main-app/components/scripts/ScriptLoadingText';
import ScriptViewScheduleHolder from '@/main-app/components/scripts/ScriptViewScheduleHolder';
import DOMPurify from 'dompurify';
import {marked} from 'marked';
import {mapActions, mapState} from 'vuex'
import {STATUS_DISCONNECTED, STATUS_ERROR, STATUS_EXECUTING, STATUS_FINISHED} from '../../store/scriptExecutor';
import ScriptParametersView from './script-parameters-view'

export default {
  data: function () {
    return {
      id: null,
      everStarted: false,
      shownErrors: [],
      nextLogIndex: 0,
      lastInlineImages: {},
      scheduleMode: false,
      scriptConfigComponentsHeight: 0,
      parametersExpanded: true,
      commandHistory: [],
      historyIndex: -1,
      currentInputDraft: ''
    }
  },

  props: {
    hideExecutionControls: Boolean
  },

  mounted: function () {
    this.id = 'script-panel-' + this._uid;
  },

  components: {
    ScriptLoadingText,
    LogPanel,
    ScriptParametersView,
    ScheduleButton,
    ScriptViewScheduleHolder
  },

  computed: {
    ...mapState('scriptConfig', {
      scriptDescription: state => state.scriptConfig ? state.scriptConfig.description : '',
      loading: 'loading',
      scriptConfig: 'scriptConfig',
      parameters: 'parameters',
      outputFormat: state => state.scriptConfig ? state.scriptConfig.outputFormat : undefined,
      preloadOutput: state => state.preloadScript?.['output'],
      preloadOutputFormat: state => state.preloadScript?.['format']
    }),
    ...mapState('scriptSetup', {
      parameterErrors: 'errors'
    }),
    ...mapState('executions', {
      currentExecutor: 'currentExecutor'
    }),
    ...mapState('scripts', ['selectedScript']),

    hasErrors: function () {
      return !isNull(this.shownErrors) && (this.shownErrors.length > 0);
    },

    parameterCount() {
      return this.parameters ? this.parameters.length : 0;
    },

    canCollapseParameters() {
      return this.parameterCount > 2;
    },

    isExecuting() {
      return this.status === STATUS_EXECUTING;
    },

    formattedDescription: function () {
      if (isEmptyString(this.scriptDescription)) {
        return '';
      }

      const descriptionHtml = DOMPurify.sanitize(marked.parse(this.scriptDescription, {gfm: true, breaks: true}));
      const paragraphRemoval = document.createElement('div');
      paragraphRemoval.innerHTML = descriptionHtml.trim();

      for (var i = 0; i < paragraphRemoval.childNodes.length; i++) {
        var child = paragraphRemoval.childNodes[i];
        if (child.tagName === 'P') {
          i += child.childNodes.length - 1;

          while (child.childNodes.length > 0) {
            paragraphRemoval.insertBefore(child.firstChild, child);
          }

          paragraphRemoval.removeChild(child);
        }
      }

      return paragraphRemoval.innerHTML;
    },

    enableExecuteButton() {
      if (this.scheduleMode) {
        return false;
      }

      if (this.hideExecutionControls) {
        return false;
      }

      if (this.loading) {
        return false;
      }

      if (isNull(this.currentExecutor)) {
        return true;
      }

      return this.currentExecutor.state.status === STATUS_FINISHED
          || this.currentExecutor.state.status === STATUS_DISCONNECTED
          || this.currentExecutor.state.status === STATUS_ERROR;
    },

    enableScheduleButton() {
      if (this.hideExecutionControls) {
        return false;
      }

      if (this.loading) {
        return false;
      }

      if (isNull(this.currentExecutor)) {
        return true;
      }

      return this.currentExecutor.state.status === STATUS_FINISHED
          || this.currentExecutor.state.status === STATUS_DISCONNECTED
          || this.currentExecutor.state.status === STATUS_ERROR;
    },

    enableStopButton() {
      return this.status === STATUS_EXECUTING;
    },

    stopButtonLabel() {
      if (this.status === STATUS_EXECUTING) {
        if (this.killEnabled) {
          return 'Kill';
        }

        if (!isNull(this.killEnabledTimeout)) {
          return 'Stop (' + this.killEnabledTimeout + ')';
        }
      }

      return 'Stop';
    },

    status() {
      return isNull(this.currentExecutor) ? null : this.currentExecutor.state.status;
    },

    showLog() {
      return !isNull(this.currentExecutor) && !this.scheduleMode;
    },

    downloadableFiles() {
      if (!this.currentExecutor) {
        return [];
      }

      return this.currentExecutor.state.downloadableFiles;
    },

    inlineImages() {
      if (!this.currentExecutor) {
        return {};
      }

      return this.currentExecutor.state.inlineImages;
    },

    inputPromptText() {
      if (this.status !== STATUS_EXECUTING) {
        return null;
      }

      return this.currentExecutor.state.inputPromptText;
    },

    logChunks() {
      if (!this.currentExecutor) {
        return [];
      }

      return this.currentExecutor.state.logChunks;
    },

    killEnabled() {
      return !isNull(this.currentExecutor) && this.currentExecutor.state.killEnabled;
    },

    killEnabledTimeout() {
      return isNull(this.currentExecutor) ? null : this.currentExecutor.state.killTimeoutSec;
    },

    schedulable() {
      return this.scriptConfig && this.scriptConfig.schedulable;
    }
  },

  methods: {
    inputKeyUpHandler: function (event) {
      if (event.keyCode === 13) {
        this.submitManualInput();
      }
    },

    submitManualInput: function () {
      const inputField = this.$refs.inputField;
      const value = inputField.value;

      if (!value || !value.trim()) {
        return;
      }

      const trimmedValue = value.trim();
      this.handleUserInput(trimmedValue);

      // 保存到历史记录
      if (this.commandHistory[this.commandHistory.length - 1] !== trimmedValue) {
        this.commandHistory.push(trimmedValue);
      }
      this.historyIndex = -1;
      this.currentInputDraft = '';

      inputField.value = '';
    },

    navigateHistory: function (direction) {
      if (this.commandHistory.length === 0) return;

      if (this.historyIndex === -1) {
        this.currentInputDraft = this.$refs.inputField.value;
      }

      if (direction === 'up') {
        if (this.historyIndex === -1) {
          this.historyIndex = this.commandHistory.length - 1;
        } else if (this.historyIndex > 0) {
          this.historyIndex--;
        }
      } else if (direction === 'down') {
        if (this.historyIndex !== -1) {
          if (this.historyIndex < this.commandHistory.length - 1) {
            this.historyIndex++;
          } else {
            this.historyIndex = -1;
          }
        }
      }

      if (this.historyIndex === -1) {
        this.$refs.inputField.value = this.currentInputDraft;
      } else {
        this.$refs.inputField.value = this.commandHistory[this.historyIndex];
      }

      // 将光标移到末尾
      this.$nextTick(() => {
        const input = this.$refs.inputField;
        input.selectionStart = input.selectionEnd = input.value.length;
      });
    },

    handleInputChange: function () {
      if (this.historyIndex === -1) {
        this.currentInputDraft = this.$refs.inputField.value;
      }
    },

    validatePreExecution: function () {
      this.shownErrors = [];

      const errors = this.parameterErrors;
      if (!isEmptyObject(errors)) {
        forEachKeyValue(errors, (paramName, error) => {
          this.shownErrors.push(paramName + ': ' + error);
        });
        return false;
      }

      return true;
    },

    toggleParameters() {
      this.parametersExpanded = !this.parametersExpanded;
    },

    executeScript: function () {
      if (!this.validatePreExecution()) {
        this.parametersExpanded = true;
        return;
      }

      if (this.canCollapseParameters && this.parameterCount > 4) {
        this.parametersExpanded = false;
      }

      this.startExecution();
    },

    openSchedule: function () {
      if (!this.validatePreExecution()) {
        return;
      }

      this.$refs.scheduleHolder.open();
      this.scheduleMode = true;
    },

    ...mapActions('executions', {
      startExecution: 'startExecution'
    }),

    stopScript() {
      if (isNull(this.currentExecutor)) {
        return;
      }

      if (this.killEnabled) {
        this.$store.dispatch('executions/' + this.currentExecutor.state.id + '/killExecution');
      } else {
        this.$store.dispatch('executions/' + this.currentExecutor.state.id + '/stopExecution');
      }
    },

    handleUserInput(value) {
      this.sendUserInput(value);
    },

    copyLogToClipboard: function () {
      if (this.$refs.logPanel) {
        this.$refs.logPanel.copyLogToClipboard();
      }
    },

    downloadLog: function () {
      if (this.$refs.logPanel) {
        this.$refs.logPanel.downloadLog();
      }
    },

    toggleFullscreen: function () {
      if (this.$refs.logPanel) {
        this.$refs.logPanel.toggleFullscreen();
      }
    },

    sendUserInput(value) {
      if (isNull(this.currentExecutor)) {
        return;
      }

      this.$store.dispatch('executions/' + this.currentExecutor.state.id + '/sendUserInput', value);
    },

    setLog: function (text) {
      if (this.$refs.logPanel) {
        this.$refs.logPanel.setLog(text);
      }
    },

    appendLog: function (text) {
      if (this.$refs.logPanel) {
        this.$refs.logPanel.appendLog(text);
      }
    },


  },

  watch: {
    inputPromptText: function (value) {
      if (isNull(value) && isNull(this.$refs.inputField)) {
        return;
      }

      var fieldUpdater = function () {
        this.$refs.inputField.value = '';
        if (!isNull(value)) {
          this.$refs.inputField.focus();
        }
      }.bind(this);

      if (this.$refs.inputField) {
        fieldUpdater();
      } else {
        this.$nextTick(fieldUpdater);
      }
    },

    logChunks: {
      immediate: true,
      handler(newValue, oldValue) {
        const updateLog = () => {
          if (isNull(newValue)) {
            this.setLog('');
            this.nextLogIndex = 0;

            return;
          }

          if (newValue !== oldValue) {
            this.setLog('');
            this.nextLogIndex = 0;
          }

          for (; this.nextLogIndex < newValue.length; this.nextLogIndex++) {
            const logChunk = newValue[this.nextLogIndex];

            this.appendLog(logChunk);
          }
        }

        if (isNull(this.$refs.logPanel)) {
          this.$nextTick(updateLog);
        } else {
          updateLog();
        }
      }
    },

    preloadOutput: {
      immediate: true,
      handler(newValue) {
        this.$nextTick(() => {
          if (this.$refs.preloadOutputPanel) {
            this.$refs.preloadOutputPanel.setLog(newValue);
          }
        })
      }
    },

    inlineImages: {
      handler(newValue, oldValue) {
        const logPanel = this.$refs.logPanel;

        forEachKeyValue(this.lastInlineImages, (key, value) => {
          if (!newValue.hasOwnProperty(key)) {
            logPanel.removeInlineImage(key);
          } else if (value !== newValue[key]) {
            logPanel.setInlineImage(key, value);
          }
        });

        forEachKeyValue(newValue, (key, value) => {
          if (!this.lastInlineImages.hasOwnProperty(key)) {
            logPanel.setInlineImage(key, value);
          }
        });

        this.lastInlineImages = deepCloneObject(newValue);
      }
    },

    scriptConfig: {
      immediate: true,
      handler() {
        this.shownErrors = []
        this.parametersExpanded = true;

        this.$nextTick(() => {
          const otherElemsHeight = 200;

          if (isNull(this.$refs.parametersView)) {
            this.scriptConfigComponentsHeight = otherElemsHeight;
            return;
          }

          const paramHeight = this.$refs.parametersView.$el.clientHeight;

          this.scriptConfigComponentsHeight = paramHeight + otherElemsHeight;
        })
      }
    },

    status: {
      handler(newStatus) {
        if (newStatus === STATUS_EXECUTING && this.canCollapseParameters && this.parameterCount > 4) {
          this.parametersExpanded = false;
        }

        if (newStatus === STATUS_FINISHED) {
          this.$store.dispatch('executions/' + this.currentExecutor.state.id + '/cleanup');
        }
      }
    }
  }
}
</script>

<style scoped>

.script-view {
  display: flex;
  flex-direction: column;
  flex: 1 1 0;
  min-height: 0;
}

.script-description,
.script-loading-text {
  margin: 0 0 12px;
  padding: 10px 14px;
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--font-color-medium);
  background: var(--background-color-slight-emphasis);
  border-radius: 6px;
  border-left: 3px solid var(--primary-color);
}

.script-workspace {
  display: flex;
  flex-direction: column;
  flex: 1 1 0;
  min-height: 0;
  border: 1px solid var(--separator-color);
  border-radius: 8px;
  overflow: hidden;
  background: var(--background-color);
}

/* ── Top config zone ── */

.config-zone {
  flex-shrink: 0;
  border-bottom: 1px solid var(--separator-color);
}

.config-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 12px;
  flex-wrap: wrap;
  background: transparent;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.collapse-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border-radius: 4px;
  color: var(--font-color-medium);
  background: transparent;
  border: 1px solid var(--separator-color);
}

.collapse-toggle:hover {
  color: var(--primary-color);
  border-color: var(--primary-color);
  background: transparent;
}

.collapse-toggle .material-icons {
  font-size: 1.2rem;
}

.config-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--font-color-main);
}

.panel-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--primary-color);
  background: rgba(38, 166, 154, 0.12);
  border: 1px solid rgba(38, 166, 154, 0.25);
}

.execution-status-inline {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 4px;
  padding-left: 10px;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--font-color-medium);
  border-left: 1px solid var(--separator-color);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary-color);
  flex-shrink: 0;
  animation: status-breathe 1.8s ease-in-out infinite;
}

@keyframes status-breathe {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 0 0 rgba(38, 166, 154, 0.45);
  }
  50% {
    opacity: 0.45;
    box-shadow: 0 0 0 4px rgba(38, 166, 154, 0.15);
  }
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.button-execute,
.button-stop {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 32px;
  padding: 0 14px;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  text-transform: none;
  box-shadow: none;
  transition: background 0.15s;
}

.button-execute {
  color: var(--font-on-primary-color-main);
  background: var(--primary-color);
}

.button-execute:hover:not([disabled]) {
  background: var(--primary-color-raised-hover-solid);
}

.button-execute[disabled] {
  opacity: 0.45;
  cursor: not-allowed;
}

.button-execute .material-icons {
  font-size: 1.05rem;
}

.button-stop {
  color: #fff;
  background: #ef5350;
}

.button-stop:hover {
  background: #e53935;
}

.button-stop.kill-mode {
  background: #c62828;
}

.button-stop .material-icons {
  font-size: 1.1rem;
}

.toolbar-actions >>> .schedule-action {
  height: 36px;
  line-height: 36px;
  margin: 0;
  border-radius: 6px;
}

.config-body {
  max-height: 40vh;
  overflow-y: auto;
  overflow-x: visible;
  border-top: 1px solid var(--separator-color);
  transition: max-height 0.25s ease, opacity 0.2s ease;
}

.config-body.is-collapsed {
  max-height: 0;
  overflow: hidden;
  border-top: none;
  opacity: 0;
}

.config-collapsed-hint {
  padding: 6px 14px 8px;
  font-size: 0.8rem;
  color: var(--font-color-disabled);
  border-top: 1px solid var(--separator-color);
}

.validation-panel {
  margin: 0 12px 10px;
  padding: 8px 0 0;
  border-top: 1px solid rgba(239, 83, 80, 0.35);
}

.validation-panel-title {
  margin-bottom: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #e53935;
}

.validation-errors-list {
  margin: 0;
  padding-left: 16px;
  border-left: 1px solid rgba(239, 83, 80, 0.25);
}

.validation-errors-list li {
  color: #e53935;
  font-size: 0.78rem;
  line-height: 1.5;
}

/* ── Output panel (bottom) ── */

.output-panel {
  flex: 1 1 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.output-panel-body {
  flex: 1 1 0;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 0 12px;
}

.output-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--font-color-disabled);
  user-select: none;
}

.output-placeholder .material-icons {
  font-size: 3rem;
  opacity: 0.35;
}

.output-placeholder p {
  margin: 0;
  font-size: 0.9rem;
}

.script-view >>> .log-panel {
  flex: 1 1 0;
  min-height: 0;
  margin-top: 8px;
}

.files-download-panel {
  flex-shrink: 0;
  padding: 8px 12px;
  border-top: 1px solid var(--separator-color);
}

.files-download-panel a {
  color: var(--primary-color);
  padding-left: 12px;
  padding-right: 12px;
  margin-right: 6px;
  text-transform: none;
  font-size: 0.88rem;
}

.files-download-panel a > i {
  margin-left: 6px;
  vertical-align: middle;
  font-size: 1.3em;
}

.script-input-panel {
  flex-shrink: 0;
  margin: 0 12px 12px;
  padding-top: 8px;
  border-top: 1px solid var(--separator-color);
}

.script-input-panel .input-outer-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.script-input-panel .input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  background: #1e1e1e;
  border-radius: 8px;
  border: 1px solid #333;
  padding: 0 12px;
  height: 42px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.script-input-panel .input-wrapper:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(38, 166, 154, 0.15);
}

.script-input-panel .linux-prompt {
  color: #4caf50;
  font-family: 'Courier New', Courier, monospace;
  font-weight: bold;
  font-size: 1rem;
  margin-right: 8px;
  user-select: none;
  height: 100%;
  display: flex;
  align-items: center;
}

.script-input-panel .script-input-field {
  flex: 1;
  background: transparent;
  border: none !important;
  box-shadow: none !important;
  color: #e0e0e0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 1rem;
  padding: 0 40px 0 0;
  margin: 0;
  outline: none;
  border-radius: 0;
  height: 100%;
  display: flex;
  align-items: center;
  caret-color: #fff;
}

.script-input-panel .action-buttons {
  position: absolute;
  right: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(45, 45, 45, 0.8);
  padding: 4px;
  border-radius: 6px;
  z-index: 11;
}

.script-input-panel .divider-vertical {
  width: 1px;
  height: 16px;
  background: #444;
  margin: 0 2px;
}

.script-input-panel .action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  cursor: pointer;
  border-radius: 4px;
  color: #888;
  transition: all 0.2s ease;
}

.script-input-panel .action-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.script-input-panel .action-button i {
  font-size: 16px;
}

.script-input-panel .send-button {
  padding: 0;
  width: 28px;
  height: 28px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.script-input-panel .send-button:hover {
  filter: brightness(1.1);
}

.script-input-panel .send-button i {
  font-size: 14px;
}

@media (max-width: 600px) {
  .config-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left {
    justify-content: space-between;
  }

  .toolbar-actions {
    justify-content: stretch;
  }

  .button-execute,
  .button-stop {
    flex: 1;
  }

  .config-body {
    max-height: 45vh;
  }
}

</style>
