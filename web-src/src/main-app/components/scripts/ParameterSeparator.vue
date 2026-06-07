<template>
  <div v-trim-text
       :class="{'margin-top': !!separator.title}"
       class="parameter-separator">
    <div v-if="separator.title" class="separator-title">
      <h6>{{ separator.title }}</h6>
    </div>
    <div v-if="separator.type === 'line'" class="separator-line"></div>
  </div>
</template>

<script>
export default {
  name: 'ParameterSeparator',
  props: {
    separator: {
      type: Object
    }
  }
}
</script>

<style scoped>
.parameter-separator {
  display: flex;
  align-items: center;
  min-height: 1.5rem;
  gap: 12px;
}

.margin-top {
  margin-top: 4px;
}

.separator-title h6 {
  margin: 0;
  padding: 0 4px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--primary-color);
  background: rgba(38, 166, 154, 0.08);
  border-radius: 4px;
  padding: 2px 8px;
  white-space: nowrap;
}

.separator-line {
  flex: 1 1 0;
  height: 1px;
  background: linear-gradient(to right, var(--separator-color), transparent);
}

</style>
