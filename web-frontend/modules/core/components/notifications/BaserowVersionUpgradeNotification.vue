<template>
  <a
    class="notification-panel__notification-link"
    :href="notification.release_notes_url"
    target="_blank"
    rel="noopener noreferrer"
    @click="markAsReadAndHandleClick"
  >
    <div class="notification-panel__notification-content-title">
      <i18n path="versionUpgradeNotification.title" tag="span">
        <template #version>
          <strong>{{ `Baserow v${notification.data.version}` }}</strong>
        </template>
      </i18n>
    </div>
  </a>
</template>

<script>
import notificationContent from '@baserow/modules/core/mixins/notificationContent'

export default {
  name: 'BaserowVersionUpgradeNotification',
  mixins: [notificationContent],
  props: {
    notification: {
      type: Object,
      required: true,
    },
  },
}
</script>
