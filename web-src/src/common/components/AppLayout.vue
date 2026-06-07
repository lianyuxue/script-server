<template>
  <div class="app-layout">
    <div ref="appSidebar" :class="{collapsed: !showSidebar}" class="app-sidebar-outer">
      <div class="app-sidebar shadow-8dp">
        <slot name="sidebar"/>
      </div>
    </div>
    <a :class="{collapsed: !showSidebar}" :title="showSidebar ? '隐藏菜单' : '展开菜单'"
       class="sidebar-toggle-button" @click="toggleSidebar">
      <i class="material-icons">{{ showSidebar ? 'chevron_left' : 'chevron_right' }}</i>
    </a>
    <div class="app-content">
      <div ref="contentHeader"
           :class="{borderless: !hasHeader, 'shadow-8dp': hasHeader}" class="content-header">
        <slot name="header"/>
        <div v-if="loading" class="progress">
          <div class="indeterminate"></div>
        </div>
      </div>
      <div ref="contentPanel" class="content-panel">
        <slot name="content"/>
      </div>
    </div>
    <div v-show="showSidebar && narrowView" class="sidenav-overlay" @click="setSidebarVisibility(false)"></div>
  </div>
</template>

<script>

import {hasClass, isNull} from '@/common/utils/common';

export default {
  name: 'AppLayout',
  props: {
    loading: Boolean
  },
  data() {
    return {
      narrowView: false,
      showSidebar: false,
      hasHeader: false
    }
  },
  mounted() {
    const contentHeader = this.$refs.contentHeader;
    const contentPanel = this.$refs.contentPanel;

    updatedStylesBasedOnContent(contentHeader, contentPanel, this);

    const resizeListener = () => {
      const position = getComputedStyle(this.$refs.appSidebar).position;
      const wasNarrow = this.narrowView;
      this.narrowView = position === 'absolute';

      if (wasNarrow && !this.narrowView) {
        this.setSidebarVisibility(true);
      } else if (!wasNarrow && this.narrowView) {
        this.setSidebarVisibility(false);
      }
    };
    window.addEventListener('resize', resizeListener);
    resizeListener();
  },

  methods: {
    setSidebarVisibility(visible) {
      this.showSidebar = visible;
    },

    toggleSidebar() {
      this.showSidebar = !this.showSidebar;
    },

    isNarrowView() {
      return this.narrowView;
    }
  }
}

function recalculateHeight(contentHeader, appLayout, contentPanel) {
  if (!contentHeader.childNodes) {
    return;
  }

  let childrenHeight = 0;
  for (const child of Array.from(contentHeader.childNodes)) {
    if ((child.nodeType === 1) && (window.getComputedStyle(child).position === 'absolute')) {
      continue;
    }

    if (!isNull(child.offsetHeight)) {
      childrenHeight = Math.max(childrenHeight, child.offsetHeight);
    }
  }
  appLayout.hasHeader = childrenHeight >= 1;

  appLayout.$nextTick(() => {
    contentPanel.style.maxHeight = 'calc(100% - ' + contentHeader.offsetHeight + 'px)';
  });
}

function updatedStylesBasedOnContent(contentHeader, contentPanel, appLayout) {
  const mutationObserver = new MutationObserver(mutations => {
    mutations.forEach(() => {
      recalculateHeight(contentHeader, appLayout, contentPanel);
    });
  });

  mutationObserver.observe(contentHeader, {
    childList: true,
    subtree: true,
    characterData: true
  });

  appLayout.$nextTick(() => {
    recalculateHeight(contentHeader, appLayout, contentPanel);
  });
}

</script>

<style scoped>
.app-layout {
  position: relative;
  display: flex;
  height: 100vh;
  max-height: 100vh;
}

.app-sidebar-outer {
  position: relative;
  width: 300px;
  min-width: 300px;
  flex-shrink: 0;
  transition: width 0.3s, min-width 0.3s, transform 0.3s;
}

.app-sidebar-outer.collapsed {
  width: 0;
  min-width: 0;
}

.app-sidebar {
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-right: 1px solid var(--separator-color);
}

.app-sidebar-outer.collapsed .app-sidebar {
  border-right: none;
}

.sidebar-toggle-button {
  position: absolute;
  top: 50%;
  left: 286px;
  transform: translateY(-50%);
  z-index: 1001;
  transition: left 0.3s;

  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 48px;

  color: var(--font-color-main);
  background: var(--background-color);
  border: 1px solid var(--separator-color);
  border-left: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.sidebar-toggle-button.collapsed {
  left: 0;
}

.sidebar-toggle-button:hover {
  background: var(--script-header-background);
}

.sidebar-toggle-button > i {
  font-size: 1.25rem;
}

.app-content {
  flex: 1 1 0;

  display: flex;
  flex-direction: column;

  width: 100vw;
}

.content-header {
  flex: 0 0 auto;
  width: 100%;

  padding-left: 24px;

  border-bottom: 1px solid var(--separator-color);
  position: relative;

  background: var(--script-header-background);
}

.content-header.borderless {
  border-bottom: none;
}

.content-header .progress {
  margin: 0;
  bottom: -1px;
  position: absolute;
  left: 0;
}

.content-panel {
  flex: 1 1 0;
}

@media (max-width: 992px) {
  .app-sidebar-outer {
    position: absolute;
    height: 100vh;
    z-index: 999;
    width: 300px;
    min-width: 300px;
  }

  .app-sidebar-outer.collapsed {
    -webkit-transform: translateX(-105%);
    transform: translateX(-105%);
    width: 300px;
    min-width: 300px;
  }

  .sidenav-overlay {
    opacity: 1;
    display: block;
    background-color: rgba(0, 0, 0, 0.4);
    position: absolute;
    z-index: 500;
    width: 100%;
    height: 100%;
  }
}
</style>