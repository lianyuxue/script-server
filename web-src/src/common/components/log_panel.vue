<template>
  <div class="log-panel" :class="{'log-panel-fullscreen': isFullscreen}">
    <div class="log-panel-shadow"
         v-bind:class="{
             'shadow-top': !atTop && atBottom,
             'shadow-bottom': atTop && !atBottom,
             'shadow-top-bottom': !atTop && !atBottom}">
    </div>
    <div class="fullscreen-input-panel" v-if="isFullscreen && inputPromptText">
      <div class="input-container">
        <div class="input-outer-wrapper">
          <div v-if="inputStatus" class="input-status" :class="inputStatus">{{ inputStatusMessage }}</div>
          <div class="input-wrapper linux-input-wrapper">
            <span class="linux-prompt">$</span>
            <input ref="fullscreenInput"
                   class="script-input-field"
                   type="text"
                   @keydown.up.prevent="navigateHistory('up')"
                   @keydown.down.prevent="navigateHistory('down')"
                   @keyup.enter="handleFullscreenInput"
                   @input="handleInputChange">
            
            <div class="action-buttons">
              <button class="send-button waves-effect waves-light" @click="submitInput" title="发送 (Enter)">
                <i class="material-icons">send</i>
              </button>
              <div class="divider-vertical"></div>
              <a class="action-button waves-effect waves-circle" @click="copyLogToClipboard" title="复制日志">
                <i class="material-icons">content_copy</i>
              </a>
              <a class="action-button waves-effect waves-circle" @click="downloadLog" title="下载日志">
                <i class="material-icons">file_download</i>
              </a>
              <a class="action-button waves-effect waves-circle" @click="toggleFullscreen" title="退出全屏">
                <i class="material-icons">fullscreen_exit</i>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="panel-buttons" v-if="!isFullscreen">
      <a class="fullscreen-button btn-icon-flat waves-effect waves-circle" @click="toggleFullscreen" title="全屏查看">
        <i class="material-icons">fullscreen</i>
      </a>
      <a class="copy-text-button btn-icon-flat waves-effect waves-circle" @click="copyLogToClipboard" title="复制日志">
        <i class="material-icons">content_copy</i>
      </a>
      <a class="download-text-button btn-icon-flat waves-effect waves-circle" @click="downloadLog" title="下载日志">
        <i class="material-icons">file_download</i>
      </a>
    </div>
  </div>
</template>

<script>
import {copyToClipboard, isNull} from '@/common/utils/common';
import {TerminalOutput} from '@/common/components/terminal/ansi/TerminalOutput'
import {TextOutput} from '@/common/components/terminal/text/TextOutput'
import {HtmlIFrameOutput} from '@/common/components/terminal/html/HtmlIFrameOutput'
import {HtmlOutput} from '@/common/components/terminal/html/HtmlOutput'

export default {
  props: {
    'autoscrollEnabled': {
      type: Boolean,
      default: true
    },
    'outputFormat': {
      type: String,
      default: 'terminal'
    },
    'inputPromptText': {
      type: String,
      default: null
    }
  },
  data: function () {
    return {
      atBottom: false,
      atTop: false,
      mouseDown: false,
      scrollUpdater: null,
      needScrollUpdate: false,
      text: '',
      isFullscreen: false,
      inputStatus: '',
      inputStatusMessage: '',
      commandHistory: [],
      historyIndex: -1,
      currentInputDraft: ''
    }
  },

  mounted: function () {
    window.addEventListener('resize', this.revalidateScroll);

    this.scrollUpdater = window.setInterval(() => {
      if (!this.needScrollUpdate) {
        return;
      }
      this.needScrollUpdate = false;

      let autoscrolled = false;
      if (this.autoscrollEnabled) {
        autoscrolled = this.autoscroll();
      }

      if (!autoscrolled) {
        this.recalculateScrollPosition();
      }
    }, 40);

    this.renderOutputElement()
  },

  methods: {
    recalculateScrollPosition: function () {
      var logContent = this.output.element;

      var scrollTop = logContent.scrollTop;
      var newAtBottom = (scrollTop + logContent.clientHeight + 5) > (logContent.scrollHeight);
      var newAtTop = scrollTop === 0;

      // sometimes we can get scroll update (from incoming text) between autoscroll and this method
      if (!this.needScrollUpdate) {
        this.atBottom = newAtBottom;
        this.atTop = newAtTop;
      }
    },

    autoscroll: function () {
      var logContent = this.output.element;

      if ((this.atBottom) && (!this.mouseDown)) {
        logContent.scrollTop = logContent.scrollHeight;
        return true;
      }
      return false;
    },

    revalidateScroll: function () {
      this.needScrollUpdate = true;
    },

    setLog: function (text) {
      this.text = ''
      this.output.clear()

      this.recalculateScrollPosition()

      this.appendLog(text)
    },

    appendLog: function (text) {
      if (isNull(text) || (text === '')) {
        return;
      }

      this.text += text
      this.output.write(text);

      this.revalidateScroll();
    },

    removeInlineImage: function (output_path) {
      this.output.removeInlineImage(output_path);
    },

    setInlineImage: function (output_path, download_url) {
      this.output.setInlineImage(output_path, download_url);
    },

    copyLogToClipboard: function () {
      copyToClipboard(this.output.element);
    },

    downloadLog: function () {
      const content = this.output.element.innerText || this.output.element.textContent || '';
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'log-output.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },

    toggleFullscreen: function () {
      if (!this.isFullscreen) {
        const elem = this.$el;
        if (elem.requestFullscreen) {
          elem.requestFullscreen();
        } else if (elem.mozRequestFullScreen) {
          elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullscreen) {
          elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) {
          elem.msRequestFullscreen();
        }
        this.isFullscreen = true;
        
        // 监听全屏退出事件
        const onFullscreenChange = () => {
          if (!document.fullscreenElement && !document.webkitFullscreenElement &&
              !document.mozFullScreenElement && !document.msFullscreenElement) {
            this.isFullscreen = false;
            document.removeEventListener('fullscreenchange', onFullscreenChange);
            document.removeEventListener('webkitfullscreenchange', onFullscreenChange);
            document.removeEventListener('mozfullscreenchange', onFullscreenChange);
            document.removeEventListener('MSFullscreenChange', onFullscreenChange);
          }
        };
        document.addEventListener('fullscreenchange', onFullscreenChange);
        document.addEventListener('webkitfullscreenchange', onFullscreenChange);
        document.addEventListener('mozfullscreenchange', onFullscreenChange);
        document.addEventListener('MSFullscreenChange', onFullscreenChange);
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
          document.msExitFullscreen();
        }
      }
    },

    handleFullscreenInput: function (event) {
      if (event.keyCode === 13) {
        this.submitInput(event.target);
      }
    },

    submitInput: function (target) {
      const value = target.value || this.$refs.fullscreenInput?.value;
      if (!value || !value.trim()) {
        return;
      }

      const trimmedValue = value.trim();
      this.$emit('user-input', trimmedValue);

      // 保存到历史记录
      if (this.commandHistory[this.commandHistory.length - 1] !== trimmedValue) {
        this.commandHistory.push(trimmedValue);
      }
      this.historyIndex = -1;
      this.currentInputDraft = '';

      // 清空输入框并显示成功状态
      if (this.$refs.fullscreenInput) {
        this.$refs.fullscreenInput.value = '';
        this.$refs.fullscreenInput.focus();
      }

      this.inputStatus = 'success';
      this.inputStatusMessage = '✓ 已发送';

      // 2秒后清除状态
      setTimeout(() => {
        this.clearStatus();
      }, 2000);
    },

    navigateHistory: function (direction) {
      if (this.commandHistory.length === 0) return;

      if (this.historyIndex === -1) {
        this.currentInputDraft = this.$refs.fullscreenInput.value;
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
        this.$refs.fullscreenInput.value = this.currentInputDraft;
      } else {
        this.$refs.fullscreenInput.value = this.commandHistory[this.historyIndex];
      }

      // 将光标移到末尾
      this.$nextTick(() => {
        const input = this.$refs.fullscreenInput;
        input.selectionStart = input.selectionEnd = input.value.length;
      });
    },

    handleInputChange: function () {
      this.clearStatus();
      if (this.historyIndex === -1) {
        this.currentInputDraft = this.$refs.fullscreenInput.value;
      }
    },

    clearStatus: function () {
      this.inputStatus = '';
      this.inputStatusMessage = '';
    },

    autoFocusInput: function () {
      this.$nextTick(() => {
        if (this.$refs.fullscreenInput && this.isFullscreen) {
          this.$refs.fullscreenInput.focus();
        }
      });
    },

    renderOutputElement: function () {
      if (!this.output || !this.$el) {
        return
      }

      const oldOutputs = this.$el.getElementsByClassName('log-content')
      Array.from(oldOutputs).forEach(old => this.$el.removeChild(old))

      const terminal = this.output.element;
      terminal.classList.add('log-content');
      terminal.addEventListener('scroll', () => this.recalculateScrollPosition());
      terminal.addEventListener('mousedown', () => this.mouseDown = true);
      terminal.addEventListener('mouseup', () => this.mouseDown = false);

      this.$el.insertBefore(terminal, this.$el.children[0]);

      this.revalidateScroll()
    }
  },

  beforeDestroy: function () {
    window.removeEventListener('resize', this.revalidateScroll);
    window.clearInterval(this.scrollUpdater);
  },

  watch: {
    outputFormat: {
      immediate: true,
      handler: function () {
        switch (this.outputFormat) {
          case 'terminal':
            this.output = new TerminalOutput()
            break
          case 'html_iframe':
            this.output = new HtmlIFrameOutput()
            break
          case 'html':
            this.output = new HtmlOutput()
            break
          case 'text':
            this.output = new TextOutput()
            break
          default:
            console.log('WARNING! Unknown outputFormat: "' + this.outputFormat + '". Falling back to terminal')
            this.output = new TerminalOutput()
        }

        this.output.write(this.text)

        this.renderOutputElement()
      }
    },

    inputPromptText: {
      handler: function () {
        this.autoFocusInput();
      }
    },

    isFullscreen: {
      handler: function () {
        this.autoFocusInput();
      }
    }
  }
}

</script>

<style scoped>
.log-panel {
  flex: 1;

  position: relative;
  min-height: 0;

  background: var(--surface-color);

  width: 100%;

  border: solid 1px var(--separator-color);
  border-radius: 2px;
}

.log-panel-shadow {
  position: absolute;

  width: 100%;
  min-height: 100%;
  top: 0;
  z-index: 5;

  pointer-events: none;
}

.shadow-top-bottom {
  box-shadow: 0 7px 8px -4px rgba(0, 0, 0, 0.4) inset, 0 -7px 8px -4px rgba(0, 0, 0, 0.4) inset;
}

.shadow-top {
  box-shadow: 0 7px 8px -4px rgba(0, 0, 0, 0.4) inset;
}

.shadow-bottom {
  box-shadow: 0 -7px 8px -4px rgba(0, 0, 0, 0.4) inset;
}

.log-panel >>> .log-content.terminal-output img {
  max-width: 100%
}

.panel-buttons {
  position: absolute;
  right: 8px;
  bottom: 4px;
  display: flex;
  gap: 4px;
  z-index: 20;
}

.log-panel-fullscreen .panel-buttons {
  bottom: auto;
  top: 8px;
}

.log-panel .copy-text-button,
.log-panel .download-text-button,
.log-panel .fullscreen-button {
  position: relative;
  right: auto;
  bottom: auto;
}

.log-panel .copy-text-button i,
.log-panel .download-text-button i,
.log-panel .fullscreen-button i {
  color: var(--font-color-disabled);
}

.log-panel-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  width: 100vw;
  height: 100vh;
  border: none;
  border-radius: 0;
}

.log-panel-fullscreen >>> .log-content {
  padding-bottom: 100px !important;
  padding-top: 20px;
  box-sizing: border-box;
}

.fullscreen-input-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 90px;
  background: var(--surface-color);
  border-top: 1px solid var(--separator-color);
  box-shadow: 0 -4px 15px rgba(0, 0, 0, 0.15);
  z-index: 10;
  display: flex;
  flex-direction: column;
}

.input-container {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  background: #1e1e1e;
  border-radius: 8px;
  border: 1px solid #333;
  padding: 0 12px;
  height: 52px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.input-wrapper:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb, 26, 115, 232), 0.15);
}

.linux-prompt {
  color: #4caf50;
  font-family: 'Courier New', Courier, monospace;
  font-weight: bold;
  font-size: 1.1rem;
  margin-right: 8px;
  user-select: none;
  height: 100%;
  display: flex;
  align-items: center;
  padding-bottom: 2px;
}

.fullscreen-input-panel .script-input-field {
  flex: 1;
  background: transparent;
  border: none !important;
  box-shadow: none !important;
  color: #e0e0e0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 1.1rem;
  padding: 0 140px 0 0;
  margin: 0;
  outline: none;
  border-radius: 0;
  height: 100%;
  display: flex;
  align-items: center;
  caret-color: #fff;
}

.action-buttons {
  position: absolute;
  right: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(45, 45, 45, 0.8);
  padding: 4px;
  border-radius: 6px;
  z-index: 11;
}

.divider-vertical {
  width: 1px;
  height: 16px;
  background: #444;
  margin: 0 2px;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  cursor: pointer;
  border-radius: 4px;
  color: #888;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.action-button i {
  font-size: 16px;
}

.send-button {
  padding: 0;
  width: 30px;
  height: 30px;
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

.send-button:hover {
  filter: brightness(1.1);
  transform: scale(1.05);
}

.send-button i {
  font-size: 16px;
}

.input-outer-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-status {
  position: absolute;
  right: calc(100% + 12px);
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
  animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  pointer-events: none;
}

.input-status.success {
  color: #4caf50;
}

.input-status.error {
  color: #f44336;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/*noinspection CssInvalidPropertyValue,CssOverwrittenProperties*/
.log-panel >>> .log-content {
  display: block;
  overflow-y: auto;
  height: 100%;
  width: 100%;

  font-size: .875em;

  padding: 1.5em;

  white-space: pre-wrap; /* CSS 3 */
  white-space: -moz-pre-wrap; /* Mozilla, since 1999 */
  white-space: -o-pre-wrap; /* Opera 7 */
  overflow-wrap: break-word;

  -ms-word-break: break-all;
  /* This is the dangerous one in WebKit, as it breaks things wherever */
  word-break: break-all;
  /* Instead use this non-standard one: */
  word-break: break-word;

  /* Adds a hyphen where the word breaks, if supported (No Blink) */
  -ms-hyphens: auto;
  -moz-hyphens: auto;
  -webkit-hyphens: auto;
  hyphens: auto;
}
</style>
