<template>
  <div v-if="paragraphs.length">
    <p
      v-for="paragraph in paragraphs"
      :key="paragraph.id"
      class="paragraph-element"
    >
      {{ paragraph.content }}
    </p>
  </div>
  <p v-else class="paragraph-element element--no-value">
    {{ $t('paragraphElement.noValue') }}
  </p>
</template>

<script>
import element from '@baserow/modules/builder/mixins/element'
import { generateHash } from '@baserow/modules/core/utils/hashing'

/**
 * @typedef Paragraph
 * @property {string} content - The text displayed
 * @property {string} id - The id of the paragraph hashed
 */

export default {
  name: 'ParagraphElement',
  mixins: [element],
  props: {
    /**
     * @type {Object}
     * @property {Array.<Paragraph>} value - A list of paragraphs
     */
    element: {
      type: Object,
      required: true,
    },
  },
  computed: {
    paragraphs() {
      return this.element.value
        .split('\n')
        .map((line) => line.trim())
        .filter((line) => line)
        .map((line, index) => ({
          content: line,
          id: generateHash(line + index),
        }))
    },
  },
}
</script>
